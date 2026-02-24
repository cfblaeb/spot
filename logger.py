import time
import sqlite3
import json
import os
from datetime import datetime
from bme68x import BME68X
import bme68xConstants as bme_con
import bsecConstants as bsec_con

DB_FILE = "airquality.db"
STATE_FILE = "bsec_state.json"

def setup_database():
    """Creates the SQLite database and table with the eCO2 column."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS sensor_data (
                                                              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                              temperature REAL,
                                                              humidity REAL,
                                                              pressure REAL,
                                                              iaq REAL,
                                                              eco2 REAL,
                                                              accuracy INTEGER
                   )
                   ''')
    conn.commit()
    conn.close()

def print_startup_splash(sensor):
    """Prints diagnostic information from the chip and library."""
    print("=" * 55)
    print(" 🌬️  BME680 Data Logger - Startup Splash ")
    print("=" * 55)

    # Attempt to read Chip ID
    try:
        chip_id = sensor.get_chip_id()
        # Chip ID is usually returned as an integer, 0x61 for BME680
        print(f"  Chip ID:        {hex(chip_id) if isinstance(chip_id, int) else chip_id}")
    except Exception as e:
        print(f"  Chip ID:        Not available ({e})")

    # Attempt to read Sensor Variant (Usually returns 'BME680' or 'BME688')
    try:
        variant = sensor.get_variant()
        print(f"  Sensor Variant: {variant}")
    except Exception as e:
        print(f"  Sensor Variant: Not available ({e})")

    # Attempt to read BSEC Version
    try:
        bsec_ver = sensor.get_bsec_version()
        print(f"  BSEC Version:   {bsec_ver}")
    except Exception as e:
        print(f"  BSEC Version:   Not available ({e})")

    print("=" * 55)

def main():
    setup_database()

    # Initialize sensor (If you get an I2C error, swap to BME68X_I2C_ADDR_HIGH)
    sensor = BME68X(bme_con.BME68X_I2C_ADDR_LOW, 1)

    # Print the requested startup splash info
    print_startup_splash(sensor)

    # Set to Low Power mode (1 measurement every 3 seconds) for robust BSEC calibration
    sensor.set_sample_rate(bsec_con.BSEC_SAMPLE_RATE_LP)

    # --- STATE RESTORATION ---
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state_data = json.load(f)
                sensor.set_bsec_state(state_data)
            print("✅ Successfully loaded previous BSEC state. Skipping full recalibration.")
        except Exception as e:
            print(f"⚠️ Could not load BSEC state (file might be corrupted): {e}")
    else:
        print("ℹ️ No previous BSEC state found. Starting fresh calibration.")

    print("🚀 Started logging! (LP Mode active, averaging & saving state every 5 mins)...")

    # Timers and accumulation buffer (lists acting as our smoothing buffer)
    last_log_time = time.time()
    t_buf, h_buf, p_buf, iaq_buf, eco2_buf = [], [], [], [], []

    while True:
        try:
            # Continuously poll the sensor every 3 seconds so BSEC algorithm can crunch numbers
            data = sensor.get_bsec_data()

            if data:
                # 1. Accumulate the environmental data into our buffer
                t_buf.append(data.get('temperature', 0.0))
                h_buf.append(data.get('humidity', 0.0))
                p_buf.append(data.get('raw_pressure', 0.0) / 100) # Convert Pascals to hPa
                iaq_buf.append(data.get('iaq', 0.0))
                eco2_buf.append(data.get('co2_equivalent', 500.0))

                # 2. Grab the EXACT accuracy state at this moment (Do NOT average this)
                latest_acc = data.get('iaq_accuracy', 0)

                current_time = time.time()

                # 3. Once 300 seconds (5 mins) have passed, calculate the mean and write to DB
                if current_time - last_log_time >= 300 and len(t_buf) > 0:

                    avg_temp = sum(t_buf) / len(t_buf)
                    avg_hum = sum(h_buf) / len(h_buf)
                    avg_press = sum(p_buf) / len(p_buf)
                    avg_iaq = sum(iaq_buf) / len(iaq_buf)
                    avg_eco2 = sum(eco2_buf) / len(eco2_buf)

                    # Insert averaged data into SQLite
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO sensor_data (temperature, humidity, pressure, iaq, eco2, accuracy) VALUES (?, ?, ?, ?, ?, ?)",
                        (avg_temp, avg_hum, avg_press, avg_iaq, avg_eco2, latest_acc)
                    )
                    conn.commit()
                    conn.close()

                    # --- STATE SAVING ---
                    try:
                        bsec_state = sensor.get_bsec_state()
                        if bsec_state:
                            with open(STATE_FILE, 'w') as f:
                                json.dump(bsec_state, f)
                    except Exception as e:
                        print(f"⚠️ Failed to save BSEC state: {e}")

                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged Avg: {avg_temp:.2f}°C, IAQ: {avg_iaq:.1f}, eCO2: {avg_eco2:.0f}ppm (Acc: {latest_acc}) | Samples: {len(t_buf)}")

                    # 4. Clear the accumulation buffer and reset the timer
                    t_buf.clear()
                    h_buf.clear()
                    p_buf.clear()
                    iaq_buf.clear()
                    eco2_buf.clear()

                    last_log_time = current_time

            # Sleep for exactly 3 seconds to keep the LP algorithm happy
            time.sleep(3)

        except Exception as e:
            print(f"Error reading sensor: {e}")
            time.sleep(3)

if __name__ == '__main__':
    main()