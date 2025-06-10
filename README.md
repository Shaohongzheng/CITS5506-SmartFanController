# Smart Fan & Heater Control System  
Raspberry Pi • BME280 • MQTT • Home Assistant

---

## 1. Project Overview
This project turns a **Raspberry Pi** into an intelligent climate controller using a **BME280 temperature / humidity sensor** plus **PWM‑driven fan and heater**.

Two operating modes are supported:

* **Auto Mode** – adjusts fan speed and heater power based on temperature thresholds.  
* **Manual Mode** – obeys commands sent from Home Assistant dashboards.

Live readings and device states are sent over **MQTT**, while a **16 × 2 character LCD** shows at‑a‑glance information on site.

---

## 2. Hardware List

| Part | Purpose | GPIO / Interface |
|------|---------|------------------|
| Raspberry Pi (40‑pin) | Main controller | — |
| BME280 module | I²C temperature & humidity sensor | SDA1 / SCL1 |
| 16 × 2 HD44780 LCD | Status display | GPIO 26, 19, 22, 10, 24, 25 |
| Brushless fan + MOSFET | PWM speed control | GPIO 18 (PWM) |
| Heater + driver | PWM power control | GPIO 27 (PWM) |
| 12 V / 5 V PSU | Power for fan, heater, LCD | — |

> **Safety note:** share a common ground and isolate high‑current loads with opto‑couplers or MOSFET drivers to protect the Pi.

---

## 3. Software Dependencies

```bash
sudo apt update && sudo apt install -y python3-pip i2c-tools
pip3 install paho-mqtt RPi.GPIO gpiozero smbus2 bme280                  adafruit-circuitpython-charlcd
```

* **MQTT Broker:** any MQTT 3.1.1 server (example IP `172.20.10.3:1883`, no auth).  
* **Home Assistant:** 2023.12 or later, configured to use the same broker.

---

## 4. Directory Structure

```
project/
├── SmartFanController.py   # main control script
└── README.md
```

---

## 5. Pre‑Run Setup

1. **Enable I²C**  
   `sudo raspi-config` → *Interface Options* → *I2C* → **Enable**  

2. **Verify wiring**  
   `i2cdetect -y 1` should show `0x77` (default BME280 address).  

3. **Start an MQTT broker** (local example):  
   ```bash
   sudo apt install mosquitto mosquitto-clients
   sudo systemctl enable --now mosquitto
   ```

4. **Add dashboard controls in Home Assistant** – see section 8 for a ready‑made YAML snippet.

---

## 6. MQTT Topic Map

| Direction | Topic | Payload | Meaning |
|-----------|-------|---------|---------|
| Pub | `home/sensor/temp`  | `26.73` | °C (float) |
| Pub | `home/sensor/hum`   | `52.41` | %RH (float) |
| Sub | `home/fan/mode`     | `auto` / `manual` | switch mode |
| Sub | `home/fan/control`  | `ON` / `OFF` | fan in manual mode |
| Sub | `home/heater/control` | `ON` / `OFF` | heater in manual mode |

---

## 7. System Logic

```text
┌────────────┐       MQTT Pub        ┌──────────────┐
│  BME280     │ ───────────────────▶ │ Home Assistant│
│  LCD        │◀───────────────────┐  user control  │
│  Fan PWM    │◀───────────────────┘                │
│  Heater PWM │                                     
└────────────┘
```

### Auto Mode thresholds

| Temperature | Fan PWM | Heater PWM |
|-------------|---------|------------|
| ≥ 28 °C     | 0.96 (speed 3) | 0 |
| 27 – 28 °C  | 0.90 (speed 2) | 0.30 (level 1) |
| 26 – 27 °C  | 0.70 (speed 1) | 0.70 (level 2) |
| < 26 °C     | 0 | 1.00 (level 3) |

**Manual Mode** simply follows `home/fan/control` and `home/heater/control`.

LCD sample line: `t:26.75c f:2 h:52.4% l:1`

---

## 8. Home Assistant example (`configuration.yaml`)

```yaml
mqtt:
  fan:
    - name: Smart Fan
      state_topic: home/fan/control
      command_topic: home/fan/control
      payload_on: "ON"
      payload_off: "OFF"

  switch:
    - name: Smart Heater
      state_topic: home/heater/control
      command_topic: home/heater/control
      payload_on: "ON"
      payload_off: "OFF"

  select:
    - name: Fan Mode
      state_topic: home/fan/mode
      command_topic: home/fan/mode
      options: ["auto", "manual"]

sensor:
  - name: Room Temperature
    state_topic: home/sensor/temp
    unit_of_measurement: "°C"
  - name: Room Humidity
    state_topic: home/sensor/hum
    unit_of_measurement: "%"
```

---

## 9. Run the Script

```bash
python3 SmartFanController.py
```

Press **Ctrl + C** to exit; the script cleans up GPIO lines automatically.

---

## 10. Troubleshooting

| Message | Likely Cause | Fix |
|---------|--------------|-----|
| `Remote I/O error` | bad I²C wiring / wrong address | double‑check SDA/SCL & `address` constant |
| Fan stuck full speed | wrong pin / driver issue | use GPIO 18/27 (hardware PWM), verify MOSFET |
| No data in Home Assistant | broker or topic mismatch | confirm IP, port, credentials, topic names |

---

## 11. Contribution

* **Author:** Shaohong Zheng (24023844), John Koh (23845086), Junchen Wang (23863688), Davinh Dang (22717235)
