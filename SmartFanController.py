import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import smbus2
import bme280
import time
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from gpiozero import PWMOutputDevice

# LCD setup
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d7 = digitalio.DigitalInOut(board.D22)
lcd_d6 = digitalio.DigitalInOut(board.D10)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_columns = 16
lcd_rows = 2
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

# Fan and Heater pin setup (PWM)
FAN_PIN = 18
HEATER_PIN = 27
fan = PWMOutputDevice(FAN_PIN)
heater = PWMOutputDevice(HEATER_PIN)

# BME280 Sensor setup
port = 1
address = 0x77
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

# Initial states
mode = "manual"
fan_manual = "OFF"
heater_manual = "OFF"

# MQTT callbacks
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print("Connected to MQTT Broker")
    client.subscribe("home/fan/mode")
    client.subscribe("home/fan/control")
    client.subscribe("home/heater/control")

def on_message(client, userdata, msg):
    global mode, fan_manual, heater_manual
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} = {payload}")

    if msg.topic == "home/fan/mode":
        if payload in ["auto", "manual"]:
            mode = payload
            print(f"Change mode to：{mode.upper()}")
    elif msg.topic == "home/fan/control":
        fan_manual = payload
    elif msg.topic == "home/heater/control":
        heater_manual = payload

# MQTT setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("172.20.10.3", 1883, 60)
client.loop_start()

# Main loop
try:
    while True:
        try:
            data = bme280.sample(bus, address, calibration_params)
            temp = round(data.temperature, 2)
            hum = round(data.humidity, 2)
            speed = 0
            light = 0

            client.publish("home/sensor/temp", temp)
            client.publish("home/sensor/hum", hum)
            print(f"Temp: {temp}°C | Hum: {hum}%")

            if mode == "auto":
                if temp >= 28:
                    fan.value = 0.96
                    speed = 3
                    print("FS: 3")
                elif temp >= 27:
                    fan.value = 0.9
                    speed = 2
                    print("FS: 2")
                elif temp >= 26:
                    fan.value = 0.7
                    speed = 1
                    print("FS: 1")
                else:
                    fan.value = 0
                    speed = 0

                if temp <= 27:
                    heater.value = 0.3
                    light = 1
                    print("H: 1")
                elif temp <= 26:
                    heater.value = 0.7
                    light = 2
                    print("H: 2")
                else:
                    heater.value = 1
                    light = 3
                    print("H: 3")

                print("AUTO: Fan and Heater controlled")

            elif mode == "manual":
                if fan_manual == "ON":
                    fan.value = 1
                    speed = 1
                    print("MANUAL: Fan ON")
                else:
                    fan.value = 0
                    speed = 0
                    print("MANUAL: Fan OFF")

                if heater_manual == "ON":
                    heater.value = 1
                    light = 1
                    print("MANUAL: Heater ON")
                else:
                    heater.value = 0
                    light = 0
                    print("MANUAL: Heater OFF")

        except Exception as e:
            print("Sensor read error:", e)

        lcd_message = f"t:{temp:.2f}c f:{speed} h:{hum:.2f}% l:{light}"
        lcd.message = lcd_message
        time.sleep(0.5)

except KeyboardInterrupt:
    fan.value = 0.0
    heater.value = 0.0
    lcd.clear()
    print("Exiting, cleaning up GPIO")
    GPIO.cleanup()
    client.disconnect()