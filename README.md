Smart Fan Controller
A smart IoT fan and heater control system built using Raspberry Pi, BME280 sensor, PWM fan/heater output, MQTT communication, and LCD display. The system supports both manual and automatic modes and integrates with Home Assistant for user control and monitoring.

📌 Features
Real-time temperature and humidity monitoring using BME280 sensor

Fan and heater control via PWM output (gpiozero)

Automatic mode adjusts fan/heater based on temperature thresholds

Manual mode allows remote ON/OFF switching via MQTT

LCD screen displays current temperature, humidity, fan speed, and heater level

MQTT integration using paho-mqtt for sensor updates and remote control

✅ Home Assistant used as the front-end interface to send control commands and view live sensor data

🧰 Technologies
Hardware: Raspberry Pi, BME280, LCD 16x2, Fan (PWM), Heater (PWM)

Language: Python

Libraries: paho-mqtt, gpiozero, bme280, adafruit_character_lcd

Platform: Home Assistant for user interaction

🛠️ How to Run
Hardware Setup

Connect BME280 to I2C pins (default address: 0x77)

Connect PWM-controlled fan to GPIO 18

Connect PWM-controlled heater to GPIO 27

Connect LCD to GPIO pins (D4–D7, RS, EN as defined in code)

Install Dependencies

pip install paho-mqtt gpiozero adafruit-circuitpython-charlcd smbus2 RPi.GPIO

Run the Program

python3 SmartFanController.py

Home Assistant Integration

Install or connect to MQTT Broker

Use Home Assistant to:

Send mode control: topic home/fan/mode, payload auto or manual

Control fan: home/fan/control, payload ON or OFF

Control heater: home/heater/control, payload ON or OFF

View sensor readings from:

home/sensor/temp (temperature)

home/sensor/hum (humidity)

📊 Data Topics Summary
Topic Payload Description
home/fan/mode auto / manual Switch between modes
home/fan/control ON / OFF Manual fan control
home/heater/control ON / OFF Manual heater control
home/sensor/temp float Temperature in °C (auto-published)
home/sensor/hum float Humidity in % (auto-published)

👨‍💻 Author
Shaohong Zheng (24023844)

📂 Project Structure
SmartFanProject/
├── SmartFanController.py # Main Python script
├── README.md # Project overview and instructions

📝 Notes
Ensure MQTT broker is accessible from Raspberry Pi (default IP: 172.20.10.3)

LCD displays: t:XX.X f:X h:XX.X l:X

Heater and fan behavior is defined by temperature thresholds in the script

📸 Screenshots (Optional)
Include setup photos or Home Assistant UI screenshots if needed.
