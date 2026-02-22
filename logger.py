import time
import sqlite3
from datetime import datetime
from bme68x import BME68X
import bme68xConstants as bme_con
import bsecConstants as bsec_con

DB_FILE = "airquality.db"

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

def main():
    setup_database()
    
    # Initialize sensor. If you get an I2C error, change BME68X_I2C_ADDR_LOW to BME68X_I2C_ADDR_HIGH
    sensor = BME68X(bme_con.BME68X_I2C_ADDR_LOW, 1)
    
    # Set to Ultra-Low Power mode (1 measurement every 300 seconds / 5 mins)
    sensor.set_sample_rate(bsec_con.BSEC_SAMPLE_RATE_ULP)

    print("Started logging BME680 data to SQLite (ULP Mode: 1 read/5 min)...")

    while True:
        try:
            data = sensor.get_bsec_data()
            if data:
                # Extract compensated values
                temp = data.get('temperature', 0.0)
                hum = data.get('humidity', 0.0)
                press = data.get('raw_pressure', 0.0) / 100  # Convert Pascals to hPa
                iaq = data.get('iaq', 0.0)
                eco2 = data.get('co2_equivalent', 500.0)     # Extract Estimated CO2
                acc = data.get('iaq_accuracy', 0)

                # Insert into SQLite
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sensor_data (temperature, humidity, pressure, iaq, eco2, accuracy) VALUES (?, ?, ?, ?, ?, ?)",
                    (temp, hum, press, iaq, eco2, acc)
                )
                conn.commit()
                conn.close()
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged: {temp:.2f}°C, IAQ: {iaq:.1f}, eCO2: {eco2:.0f}ppm (Acc: {acc})")

            # Wait exactly 5 minutes for the next ULP measurement
            time.sleep(300)
            
        except Exception as e:
            print(f"Error reading sensor: {e}")
            time.sleep(60) # Wait a minute before retrying to avoid spamming errors

if __name__ == '__main__':
    main()
