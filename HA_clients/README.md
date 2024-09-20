I'm going to experiment with creating Home Assistant compatible device clients
- A wifi based MTQQ client
- A BLE based client

plug
Main Module V. 7.0.0
MCU Module V. 7.0.0
id bfc78c2dd589f398c3tvwn
mac 10:d5:61:c8:65:c6

Device MAC address: 10:d5:61:c8:65:c6
Device Id: OL5iFG140gFZZCbVZSr8
Local Key: XPlOEVvhdlIJdcN3


pære
mm 1.0.4
mcu 1.0.4
bf72f1dfd396eeaf41o7wf
50:8a:06:39:53:2f

encrypt key
KZyYZ7B0MrMWHLqZgt8QzAMyYhAM7rnLl/TSnXIDo9Y=

Device Id: ueFGJT1fkyTSWfpf6lXE
Local Key: 4tpdM67KfTmZuP8C
Device MAC address: 50:8a:06:39:53:2f

I'm going to experiment with creating Home Assistant compatible device clients
- A wifi based MTQQ client
- A BLE based client

plug
Main Module V. 7.0.0
MCU Module V. 7.0.0
id bfc78c2dd589f398c3tvwn
mac 10:d5:61:c8:65:c6

Device MAC address: 10:d5:61:c8:65:c6
Device Id: OL5iFG140gFZZCbVZSr8
Local Key: XPlOEVvhdlIJdcN3
# Enable Home Assistant API
api:
encryption :
key: "3YnTPMo9CMOfzCOuq/AE2Brir3KUrwt05gAExXdgSWU="
ota:
platform: esphome
password: "fad1e78e3bfdf3606f1d24b664874d71"
wifi:
ssid: ! secret wifi_ssid
password: ! secret wifi_password
# Enable fallback hotspot (captive portal) in case wifi conne
ap:
ssid: "Tester Fallback Hotspot"
password: "EROjOEuLX3PI"


pære
mm 1.0.4
mcu 1.0.4
bf72f1dfd396eeaf41o7wf
50:8a:06:39:53:2f

encrypt key
KZyYZ7B0MrMWHLqZgt8QzAMyYhAM7rnLl/TSnXIDo9Y=

Device Id: ueFGJT1fkyTSWfpf6lXE
Local Key: 4tpdM67KfTmZuP8C
Device MAC address: 50:8a:06:39:53:2f
board: generic-bk7231n-qfn32-tuya
# Enable logging
Logger :



# Enable Home Assistant API
esphome:
  name: ladvance-light
  friendly_name: ladvance_light

bk72xx:
  board: generic-bk7231t-qfn32-tuya

# Enable logging
logger:

# Enable Home Assistant API
api:
  encryption:
    key: "KZyYZ7B0MrMWHLqZgt8QzAMyYhAM7rnLl/TSnXIDo9Y="

ota:
  - platform: esphome
    password: "fadf2e86c821ceca97ad850b406dec85"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Enable fallback hotspot (captive portal) in case wifi connection fails
  ap:
    ssid: "Ladvance-Light Fallback Hotspot"
    password: "p3BSnINFxuFf"

captive_portal:
    