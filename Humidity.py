
from machine import Pin
from time import sleep
import requests as rq
import time
import dht

dht_sensor = dht.DHT11(Pin(13))
buzzer_pin = Pin(14, Pin.OUT)

def dht_data():
    dht_sensor.measure() 
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    sleep(1)
    if temp > 30 or (hum > 90 or hum < 30):
        buzzer_pin.value(1)
    else:
        buzzer_pin.value(0)
    return temp,hum,temp_f
