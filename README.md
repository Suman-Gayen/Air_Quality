# 🌫️ ESP32 Air Quality & Environmental Monitoring System

A MicroPython-based IoT project that monitors **air quality**, **temperature**, and **humidity** in real time using an ESP32/ESP8266 microcontroller. Sensor data is displayed on an I²C LCD, pushed to a Firebase Realtime Database, and emailed automatically.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Project Structure](#project-structure)
- [Module Documentation](#module-documentation)
  - [air\_quality.py](#air_qualitypy)
  - [DHT11.py](#dht11py)
  - [connection.py](#connectionpy)
  - [umail.py](#umailpy)
  - [fire\_test.py](#fire_testpy)
- [Circuit Connections](#circuit-connections)
- [Configuration](#configuration)
- [Firebase Setup](#firebase-setup)
- [Email Setup](#email-setup)
- [How It Works](#how-it-works)
- [Data Format](#data-format)
- [Alerts & Thresholds](#alerts--thresholds)
- [Known Issues & Limitations](#known-issues--limitations)
- [License](#license)

---

## Overview

This project turns an ESP32 (or ESP8266) microcontroller into a full environmental monitoring node. Every cycle it:

1. Reads gas/air-quality level from an analog MQ-series sensor.
2. Reads temperature and humidity from a DHT11 sensor.
3. Shows the readings on a 16×2 I²C LCD.
4. Uploads the data to Google Firebase Realtime Database.
5. Sends a summary email via Gmail SMTP.
6. Triggers a buzzer when readings cross critical thresholds.

---

## Features

| Feature | Details |
|---|---|
| 🌡️ Temperature monitoring | Celsius and Fahrenheit |
| 💧 Humidity monitoring | Percentage (%) |
| 💨 Air / Gas quality | Percentage (0–100%) |
| 📟 LCD display | Real-time 16×2 I²C output |
| ☁️ Cloud upload | Firebase Realtime Database |
| 📧 Email alerts | Via Gmail SMTP (SSL) |
| 🔔 Buzzer alert | Triggered on threshold breach |
| 📶 Wi-Fi connectivity | Auto-reconnect on boot |

---

## Hardware Requirements

| Component | Quantity | Notes |
|---|---|---|
| ESP32 or ESP8266 | 1 | Primary microcontroller |
| DHT11 sensor | 1 | Temperature & humidity |
| MQ-series gas sensor (analog) | 1 | Air / gas quality |
| Active buzzer | 1 | Alert output |
| 16×2 I²C LCD (PCF8574 backpack) | 1 | Address `0x27` |
| Jumper wires | Several | For connections |
| Breadboard | 1 | Optional |
| 3.3V / 5V power supply | 1 | Per board requirements |

---

## Software Requirements

- [MicroPython](https://micropython.org/download/) firmware flashed on ESP32/ESP8266
- The following MicroPython libraries must be present on the device:

| Library | Purpose | Source |
|---|---|---|
| `dht` | DHT11 sensor driver | Built into MicroPython |
| `machine` | GPIO, ADC, I²C control | Built into MicroPython |
| `network` | Wi-Fi management | Built into MicroPython |
| `requests` | HTTP POST to Firebase | `urequests` / MicroPython |
| `i2c_lcd` | I²C LCD driver | Third-party MicroPython lib |
| `ubinascii` | Base64 encoding for SMTP auth | Built into MicroPython |
| `umail` | SMTP email client | Included in this project |

---

## Project Structure

```
📁 project-root/
├── fire_test.py       # Main entry point — orchestrates all modules
├── air_quality.py     # MQ sensor reader — returns air quality %
├── DHT11.py           # DHT11 reader — returns temp, humidity, buzzer control
├── connection.py      # Wi-Fi connection helper
├── umail.py           # Lightweight SMTP email client for MicroPython
└── README.md          # This file
```

---

## Module Documentation

### `air_quality.py`

Reads the analog output of an MQ-series gas/air-quality sensor connected to **ADC pin 0**.

#### Functions

---

#### `per(x, in_min, in_max, out_min, out_max) → float`

A general-purpose linear interpolation (map) function. Converts a raw ADC value from one range to another.

| Parameter | Type | Description |
|---|---|---|
| `x` | `int` | The raw input value to convert |
| `in_min` | `int` | Minimum of the input range |
| `in_max` | `int` | Maximum of the input range |
| `out_min` | `int` | Minimum of the output range |
| `out_max` | `int` | Maximum of the output range |

**Returns:** `float` — the mapped value.

---

#### `air() → int`

Reads the ADC, maps the raw value (0–1023) to a percentage (0–100), waits 1 second, and returns the air quality percentage.

> ⚠️ **Note:** The ADC read range is mapped from `0–1023`. If your board returns 12-bit ADC values (0–4095), update `in_max` to `4095` inside this function.

**Returns:** `int` — air quality as a percentage (0 = clean, 100 = heavily polluted).

**Example:**
```python
from air_quality import air
quality = air()
print(f"Air Quality: {quality}%")
```

---

### `DHT11.py`

Interfaces with the DHT11 sensor on **GPIO Pin 12** and controls a **buzzer on GPIO Pin 14**.

#### Pin Assignments

| Signal | GPIO Pin |
|---|---|
| DHT11 Data | 12 |
| Buzzer | 14 |

#### Functions

---

#### `dht_data() → tuple(int, int, float)`

Triggers a DHT11 measurement, computes Fahrenheit, activates/deactivates the buzzer based on thresholds, waits 1 second, and returns the readings.

**Returns:** `(temp_C, humidity, temp_F)`

| Return Value | Type | Description |
|---|---|---|
| `temp` | `int` | Temperature in Celsius |
| `hum` | `int` | Relative humidity in % |
| `temp_f` | `float` | Temperature in Fahrenheit |

**Buzzer Logic:**

| Condition | Buzzer State |
|---|---|
| `temp > 30°C` | ON 🔔 |
| `hum > 90%` | ON 🔔 |
| `hum < 30%` | ON 🔔 |
| All values normal | OFF |

**Example:**
```python
from DHT11 import dht_data
temp, hum, temp_f = dht_data()
print(f"Temp: {temp}°C / {temp_f}°F, Humidity: {hum}%")
```

---

### `connection.py`

Manages Wi-Fi connectivity for the ESP32/ESP8266.

#### Functions

---

#### `do_connect() → None`

Activates the station interface, connects to the configured Wi-Fi network, and blocks until a connection is established. Prints the assigned IP address on success.

> ✏️ **Modify the SSID and password** inside `fire_test.py` (see [Configuration](#configuration)).

**Example:**
```python
import connection
connection.do_connect()
```

---

### `umail.py`

A minimal MicroPython SMTP client. Supports **SSL (port 465)** and **STARTTLS**, with **PLAIN** and **LOGIN** authentication — both compatible with Gmail App Passwords.

> Original source: [uMail by Shawwwn](https://github.com/shawwwn/uMail) — MIT License.

#### Class: `SMTP`

---

#### `SMTP.__init__(host, port, ssl=False, username=None, password=None)`

Opens a TCP/SSL socket to the SMTP server and performs the initial `EHLO` handshake.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `host` | `str` | — | SMTP server hostname |
| `port` | `int` | — | SMTP port (e.g. `465` for SSL) |
| `ssl` | `bool` | `False` | Enable SSL wrapping |
| `username` | `str` | `None` | Optional — login on init |
| `password` | `str` | `None` | Optional — login on init |

---

#### `SMTP.login(username, password) → (code, resp)`

Authenticates with the server using PLAIN or LOGIN method.

---

#### `SMTP.to(addrs, mail_from=None) → (code, resp)`

Sets the sender and one or more recipients, then sends the `DATA` command to begin message body writing.

| Parameter | Type | Description |
|---|---|---|
| `addrs` | `str` or `list` | Recipient email(s) |
| `mail_from` | `str` | Sender override (defaults to logged-in username) |

---

#### `SMTP.write(content) → None`

Writes raw content to the open SMTP socket. Call multiple times to build the email body.

---

#### `SMTP.send(content='') → (code, message)`

Terminates the email with `\r\n.\r\n` and signals the server to deliver it.

---

#### `SMTP.quit() → None`

Sends `QUIT` and closes the socket connection cleanly.

**Full email example:**
```python
import umail
smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
smtp.login('you@gmail.com', 'your_app_password')
smtp.to('recipient@example.com')
smtp.write("From: ESP32 <you@gmail.com>\n")
smtp.write("Subject: Sensor Alert\n")
smtp.write("Temperature is above 30°C!")
smtp.send()
smtp.quit()
```

---

### `fire_test.py`

The **main program file**. Flash this as `main.py` on the device to run automatically on boot.

#### Execution Flow

```
Boot
 └─► do_connect()          # Connect to Wi-Fi
      └─► loop forever:
           ├─► air()            # Read air quality
           ├─► dht_data()       # Read temp + humidity
           ├─► LCD display      # Show readings on screen
           ├─► print()          # Serial console output
           ├─► send_firebase()  # POST data to Firebase
           └─► Send email       # SMTP email via umail
```

#### Internal Functions

---

#### `send_firebase(temp, hum, fer, air) → None`

Builds a timestamped JSON payload and HTTP POSTs it to the Firebase Realtime Database endpoint.

| Parameter | Type | Description |
|---|---|---|
| `temp` | `int` | Temperature in Celsius |
| `hum` | `int` | Humidity % |
| `fer` | `float` | Temperature in Fahrenheit |
| `air` | `int` | Air quality % |

**Firebase endpoint:**
```
https://air-quality-80aa6-default-rtdb.firebaseio.com/Gas_DHT11.json
```

---

## Circuit Connections

```
ESP32 / ESP8266 Pin Layout
─────────────────────────────────────────────
DHT11 sensor:
  VCC  ──► 3.3V
  GND  ──► GND
  DATA ──► GPIO 12

MQ Gas Sensor (Analog):
  VCC  ──► 3.3V / 5V
  GND  ──► GND
  AOUT ──► ADC0 (A0)

Active Buzzer:
  (+)  ──► GPIO 14
  (-)  ──► GND

I²C LCD (PCF8574 backpack):
  VCC  ──► 3.3V / 5V
  GND  ──► GND
  SDA  ──► GPIO 4
  SCL  ──► GPIO 5
─────────────────────────────────────────────
```

---

## Configuration

All user-configurable values live at the **top of `fire_test.py`**:

```python
# ── Wi-Fi ──────────────────────────────────────
ssid              = 'YOUR_WIFI_SSID'
password          = 'YOUR_WIFI_PASSWORD'

# ── Email ──────────────────────────────────────
sender_email      = 'your_sender@gmail.com'
sender_name       = 'ESP32'
sender_app_password = 'xxxx xxxx xxxx xxxx'   # Gmail App Password
recipient_email   = 'recipient@gmail.com'
email_subject     = 'Air Quality Report'

# ── LCD ────────────────────────────────────────
I2C_ADDR          = 0x27    # Change to 0x3F if LCD not found
totalRows         = 2
totalColumns      = 16

# ── Firebase ───────────────────────────────────
# Edit the URL inside send_firebase() to point to your own project
api = "https://<YOUR-PROJECT>.firebaseio.com/Gas_DHT11.json"
```

---

## Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. Navigate to **Build → Realtime Database** and create a database.
3. Set Rules to allow writes (for testing):
   ```json
   {
     "rules": {
       ".read": "auth != null",
       ".write": true
     }
   }
   ```
4. Copy your database URL and replace the `api` variable in `send_firebase()`.

Each record pushed will look like:

```json
{
  "Temperature": 28,
  "DHT11": 65,
  "Temp_F": 82.4,
  "Abnormal_Air": 42,
  "date": "24/3/2026",
  "time": "10:30:15"
}
```

---

## Email Setup

This project uses **Gmail SMTP** with an App Password (not your regular Gmail password).

1. Enable **2-Step Verification** on your Google account.
2. Go to **Google Account → Security → App Passwords**.
3. Create a new App Password (select "Mail" and "Other (custom name)").
4. Copy the 16-character password into `sender_app_password` in `fire_test.py`.

> 🔒 **Security note:** Never commit real credentials to a public repository. Consider storing credentials in a separate `config.py` that is excluded from version control.

---

## How It Works

```
┌─────────────┐     ADC read      ┌──────────────────┐
│  MQ Sensor  │ ────────────────► │  air_quality.py  │ ── air quality % ──┐
└─────────────┘                   └──────────────────┘                    │
                                                                           ▼
┌─────────────┐    GPIO read      ┌──────────────────┐             ┌─────────────┐
│   DHT11     │ ────────────────► │    DHT11.py      │ ─ T, H, F ─►│ fire_test   │
└─────────────┘                   └──────────────────┘             │  .py (main) │
                                                                    └──────┬──────┘
┌─────────────┐    I²C write      ┌──────────────────┐                    │
│  16x2 LCD   │ ◄──────────────── │  i2c_lcd lib     │ ◄──────────────────┤
└─────────────┘                   └──────────────────┘                    │
                                                                           │
┌─────────────┐   HTTP POST       ┌──────────────────┐                    │
│  Firebase   │ ◄──────────────── │  requests lib    │ ◄──────────────────┤
└─────────────┘                   └──────────────────┘                    │
                                                                           │
┌─────────────┐   SMTP / SSL      ┌──────────────────┐                    │
│   Gmail     │ ◄──────────────── │    umail.py      │ ◄──────────────────┘
└─────────────┘                   └──────────────────┘
```

---

## Data Format

### Serial Console Output (every cycle)
```
Today Weather and Gas Level Update from Air :
Temp_C  -> 27°C
Temp_F  -> 80.6F
Abnormal_Air --> 35%
Hum     --> 68%
```

### LCD Output
```
┌────────────────┐
│ Temp.:27C      │
│ Hum:68% Air:35 │
└────────────────┘
```

### Email Body
```
Today Weather and Gas Level Update from Air :
Temp_C  -> 27°C
Temp_F  -> 80.6F
Abnormal_Air --> 35%
Hum     --> 68%
```

---

## Alerts & Thresholds

| Sensor | Parameter | Threshold | Action |
|---|---|---|---|
| DHT11 | Temperature | > 30 °C | Buzzer ON |
| DHT11 | Humidity | > 90 % | Buzzer ON |
| DHT11 | Humidity | < 30 % | Buzzer ON |
| MQ Sensor | Air Quality | — | Logged only (no auto-alert) |

> 💡 You can extend the alerting logic in `DHT11.py` by modifying the `if/else` block inside `dht_data()`.

---

## Known Issues & Limitations

| Issue | Details |
|---|---|
| **Email on every cycle** | An email is sent every loop iteration, which may trigger Gmail rate limits quickly. Consider adding a counter or time check to send emails only when thresholds are breached or at set intervals. |
| **ADC range mismatch** | `air_quality.py` maps to `0–1023` but ESP32 ADC is 12-bit (`0–4095`). Update `in_max` in `per()` to `4095` for accurate readings on ESP32. |
| **Hardcoded credentials** | Wi-Fi and email credentials are stored in plain text. Use a `secrets.py` or `config.py` file and add it to `.gitignore`. |
| **NTP not configured** | Timestamps rely on `time.localtime()`, which may return incorrect values without NTP sync. Add `ntptime.settime()` after connecting to Wi-Fi. |
| **No retry on email failure** | If the SMTP connection fails, the main loop will crash. Wrap the email block in a `try/except`. |
| **Firebase write rules** | Open write rules are insecure for production. Add Firebase Authentication before deploying. |

---

## License

- `umail.py` — MIT License © 2018 [Shawwwn](https://github.com/shawwwn/uMail)
- All other files — MIT License © 2025 Project Contributors
