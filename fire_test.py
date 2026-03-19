import air_quality 
import Humidity
import connection
import requests as rq
import time
from time import sleep

import machine
from machine import Pin, SoftI2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=10000)     #initializing the I2C method for ESP32
#i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)       #initializing the I2C method for ESP8266

lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

T,H,F = Humidity.dht_data()
connection.do_connect()

def send_firebase(temp,hum,fer,air):
    t = time.localtime()
    y = t[0]
    m = t[1]
    d = t[2]
    h = t[3]
    mi= t[4]
    s = t[5]

    date = f"{d}/{m}/{y}"
    ti = f"{h}:{mi}:{s}"
    payload = {
     'Temperature' : temp,
     'Humidity' :  hum,
     'Temp_F' : fer,
     "Abnormal_Air" : air,
     'date' : date,
     'time' : ti
    }

    api = "https://air-quality-80aa6-default-rtdb.firebaseio.com/air_quality_measure.json"
    r = rq.post(api,json=payload).text

while True:
    a = air_quality.air()
    
    p1 = f"Temp.:{str(T)}°C      "
    p2 = f"Hum:{H}% Air:{a}"
    
    lcd.putstr(p1)
    lcd.putstr(p2)
    sleep(2)
    lcd.clear()
    print(f"Temp_C -> {T}℃\nTemp_F -> {F}F\nAbnormal_Air --> {a}%\nHum --> {H}%")
    send_firebase(T,H,F,a)
    sleep(2)
    print('Data Successfully Uploded.')