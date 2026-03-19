from machine import ADC
from time import sleep

s = ADC(0)
def per(x,in_min,in_max,out_min,out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def air():
    raw_value = s.read()
    # Convert raw value (0–4095) to percentage
    air_data = int(per(raw_value,0,1023,0,100))
    # print(f"Raw: {raw_value} -> {air_data}%")
    sleep(1)
    return air_data
