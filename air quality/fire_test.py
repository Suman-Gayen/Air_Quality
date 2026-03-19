import air_quality 
import DHT11
import connection
import requests as rq
import time
from time import sleep

connection.do_connect()
# Email code start=============================================================================
import umail
import network
# network credentials
ssid = 'suman' # Replace with the name of  network
password = '12345678' # Replace with  network password
# Email details
sender_email = 'microcontrollerlab2025@gmail.com' # Replace with the email address of the sender
sender_name = 'ESP32' # Replace with the name of the sender
sender_app_password = 'ymvo lzpi bcsx wnok' # Replace with the app password of the sender's email account
#recipient_email ='adarshsah1908@gmail.com' # Replace with the email address of the recipient
recipient_email ='sumangayen831@gmail.com'
#recipient_email ='avramondal70@gmail.com' 
email_subject ='Test Email' # Subject of the email
# email code end==============================================================================

# LCD Display  code start==========================================================================
import machine
from machine import Pin, SoftI2C
from i2c_lcd import I2cLcd

I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16

#i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=10000)     #initializing the I2C method for ESP32
i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=400000)       #initializing the I2C method for ESP8266

lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)
# display code end===============================================================================

# Database(Firebase) code start==========================================================================
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
     'DHT11' :  hum,
     'Temp_F' : fer,
     "Abnormal_Air" : air,
     'date' : date,
     'time' : ti
    }
    #  api = "https://air-quality-80aa6-default-rtdb.firebaseio.com/air_quality_measure.json"
    api = "https://air-quality-80aa6-default-rtdb.firebaseio.com/Gas_DHT11.json"
    rq.post(api,json=payload).text
# Database(Firebase) code end ==========================================================================

while True:
    a = air_quality.air() # Call air quality data from air_quality.py file
    T,H,F = DHT11.dht_data() # Call DHt11 data from DHT11.py file
    #LCD Output code ===================================================================================
    p1 = f"Temp.:{str(T)}C       "
    p2 = f"Hum:{H}% Air:{a}"
    lcd.putstr(p1)
    lcd.putstr(p2)
    #LCD Output code end ===============================================================================
    print(f"Today Weather and Gas Lavel Update  from Air :\nTemp_C -> {T}℃\nTemp_F -> {F}F\nAbnormal_Air --> {a}%\nHum --> {H}%")
    sleep(2)
    send_firebase(T,H,F,a) #Send data on firebase
    sleep(1)
    #Email Output code start  ==================================================================================
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
    # Login to the email account using the app password
    smtp.login(sender_email, sender_app_password)
    # Specify the recipient email address
    smtp.to(recipient_email)
    # Write the email header
    smtp.write("From:" + sender_name + "<"+ sender_email+">\n")
    smtp.write("Subject:" + email_subject + "\n")
    # Write the body of the email
    smtp.write("Today Weather and Gas Lavel Update  from Air :")
    smtp.write(f"Temp_C -> {T}℃\nTemp_F -> {F}F\nAbnormal_Air --> {a}%\nHum --> {H}%")
    # Send the email
    smtp.send()
    # Quit the email session
    smtp.quit()
    #Email Output code end ==============================================================================
    lcd.clear()
    print('Data Successfully Uploded on Firebase and Email id.')
    sleep(1)