# Air Quality Monitoring System

A MicroPython-based IoT project that monitors air quality, temperature, and humidity using ESP32/ESP8266 microcontroller, displays data on an I2C LCD screen, and uploads readings to Firebase in real-time.

## 📋 Project Overview

This project integrates multiple sensors and displays to create a comprehensive environmental monitoring system:
- **Temperature & Humidity Sensor (DHT11)**: Measures ambient temperature and humidity
- **Air Quality Sensor (MQ-135)**: Detects air quality levels
- **I2C LCD Display (16x2)**: Shows real-time sensor readings
- **Buzzer Alert**: Alerts when temperature or humidity reaches abnormal levels
- **Cloud Integration**: Sends data to Firebase Realtime Database

## 📁 File Documentation

### 1. **fire_test.py** (Main Application)
**Purpose**: The main entry point of the application that orchestrates all system components.

**Key Features**:
- Initializes all sensors and display modules
- Continuously reads sensor data
- Displays data on LCD screen
- Sends data to Firebase at regular intervals
- Implements timing controls between data uploads

**Hardware Configuration**:
```
ESP32 Pin Mapping:
- GPIO13: DHT11 (Temperature/Humidity Sensor)
- GPIO14: Buzzer
- GPIO5: I2C SCL (LCD)
- GPIO4: I2C SDA (LCD)
- GPIO0: ADC0 (Air Quality Sensor)
```

**Key Functions**:
- `send_firebase(temp, hum, fer, air)`: Sends sensor data to Firebase
  - Collects current timestamp
  - Creates JSON payload with temperature, humidity, air quality
  - Posts data to Firebase Realtime Database

**Workflow**:
1. Reads temperature, humidity, and Fahrenheit from DHT sensor
2. Connects to WiFi network
3. Continuously loops:
   - Reads air quality percentage
   - Displays Temperature and Humidity on LCD
   - Prints data to console
   - Uploads to Firebase
   - Waits 2 seconds before next cycle

**Firebase Data Structure**:
```json
{
  "Temperature": 28,
  "Humidity": 65,
  "Temp_F": 82.4,
  "Abnormal_Air": 45,
  "date": "19/3/2026",
  "time": "14:30:45"
}
```

---

### 2. **Humidity.py** (DHT11 Sensor Module)
**Purpose**: Handles temperature and humidity measurements from the DHT11 sensor.

**Key Features**:
- Initializes DHT11 sensor on GPIO13
- Measures temperature in Celsius
- Measures humidity percentage
- Calculates Fahrenheit temperature
- Triggers buzzer alert for abnormal conditions
- Implements 1-second delay between measurements

**Hardware**:
- DHT11 Sensor connected to GPIO13
- Buzzer connected to GPIO14

**Key Function**: `dht_data()`

**Returns**:
- `temp`: Temperature in Celsius
- `hum`: Humidity percentage
- `temp_f`: Temperature in Fahrenheit (calculated as: (C × 9/5) + 32)

**Alert Conditions**:
- Temperature > 30°C
- Humidity > 90%
- Humidity < 30%

**Buzzer Behavior**:
- Activates (HIGH) when alert condition is met
- Deactivates (LOW) when conditions are normal

---

### 3. **air_quality.py** (Air Quality Sensor Module)
**Purpose**: Reads and processes analog air quality sensor (MQ-135) data.

**Key Features**:
- Reads raw ADC values from air quality sensor
- Converts raw analog values to percentage (0-100%)
- Implements calibration mapping from sensor range to percentage scale
- 1-second delay between readings

**Hardware**:
- MQ-135 Air Quality Sensor connected to ADC0 (GPIO36)

**Key Function**: `per(x, in_min, in_max, out_min, out_max)`
- Maps input value from one range to another
- **Formula**: `(x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min`
- **Used for**: Converting raw ADC readings (0-4095) to percentage (0-100%)

**Key Function**: `air()`
- Reads raw sensor value from ADC
- Converts to percentage (0-100%)
- Returns integer percentage value

**Calibration**:
- Input range: 0-1023 (raw ADC values)
- Output range: 0-100 (percentage)

---

### 4. **connection.py** (WiFi Connection Module)
**Purpose**: Manages WiFi connectivity for the microcontroller.

**Key Features**:
- Establishes connection to WiFi network
- Handles connection retries with status feedback
- Displays network configuration details
- Provides reusable connection function

**WiFi Configuration**:
```python
SSID: "suman"
Password: "12345678"
```

**Key Function**: `do_connect()`
- Activates WiFi (STA mode)
- Checks if already connected
- Attempts connection with provided credentials
- Displays status dots while connecting
- Prints assigned IP address after successful connection

**Status Output**:
- Shows "connecting to network..."
- Prints dots (.) for each connection attempt
- Displays assigned IPv4 address upon successful connection

---

### 5. **lcd_api.py** (LCD API - HD44780 Controller)
**Purpose**: Provides high-level API for communicating with HD44780 compatible character LCDs.

**Key Features**:
- Abstract API independent of hardware communication method
- HD44780 command set implementation
- Cursor and display control
- Backlight management
- Custom character support (CGRAM)
- Display positioning and text output

**Main Class**: `LcdApi`

**Key Constants** (HD44780 Commands):
- `LCD_CLR`: Clear display
- `LCD_HOME`: Return to home position
- `LCD_ENTRY_MODE`: Set entry mode (increment/shift)
- `LCD_ON_CTRL`: Turn LCD/cursor on/off
- `LCD_FUNCTION`: Function set (8-bit/4-bit, lines, font)
- `LCD_CGRAM`: Set CG RAM address
- `LCD_DDRAM`: Set DD RAM address

**Key Methods**:
- `clear()`: Clear display and reset cursor to (0,0)
- `show_cursor()` / `hide_cursor()`: Toggle cursor visibility
- `blink_cursor_on()` / `blink_cursor_off()`: Toggle cursor blinking
- `display_on()` / `display_off()`: Toggle display visibility
- `backlight_on()` / `backlight_off()`: Control backlight
- `move_to(cursor_x, cursor_y)`: Position cursor at (x, y)
- `putchar(char)`: Write single character
- `putstr(string)`: Write string to LCD
- `custom_char(location, charmap)`: Define custom character

**Display Specifications**:
- Supports up to 4 lines (limited to 40 columns)
- 2-line 16-column display used in this project
- Automatic line wrapping and cursor advance

---

### 6. **i2c_lcd.py** (I2C LCD Interface - HD44780 via PCF8574)
**Purpose**: Implements HD44780 LCD control via I2C using PCF8574 I2C expander.

**Key Features**:
- HD44780 LCD control through PCF8574 I2C backpack
- 4-bit mode operation
- I2C communication at 10kHz frequency
- Backlight control via I2C pin
- Memory management with garbage collection

**Hardware**:
- LCD connected to PCF8574 I2C expander (address: 0x27)
- I2C interface on ESP32: SCL=GPIO5, SDA=GPIO4
- 2x16 character display

**PCF8574 Pin Mapping**:
```
P0 (MASK_RS = 0x01): Register Select
P1 (MASK_RW = 0x02): Read/Write Select
P2 (MASK_E = 0x04):  Enable Signal
P3 (SHIFT_BACKLIGHT = 3): Backlight Control
P4-P7 (SHIFT_DATA = 4): Data Lines (4-bit mode)
```

**Main Class**: `I2cLcd(LcdApi)`

**Initialization Process**:
1. Send initial zero byte to I2C address
2. Wait 20ms for LCD powerup
3. Send reset command 3 times (4.1ms delays)
4. Switch to 4-bit mode
5. Initialize as 2-line display

**Key Methods**:
- `hal_write_init_nibble(nibble)`: Send initialization nibble
- `hal_backlight_on()`: Enable backlight via I2C
- `hal_backlight_off()`: Disable backlight via I2C
- `hal_write_command(cmd)`: Send command in 4-bit mode
- `hal_write_data(data)`: Send data in 4-bit mode

**4-bit Mode Operation**:
- Transfers commands and data in two 4-bit transfers
- High nibble sent first, then low nibble
- Enable signal (MASK_E) pulses for each nibble

**Timing**:
- Clear/Home commands: 5ms delay
- Other operations: Variable delay with garbage collection

---

## 🔧 Dependencies

### Required Libraries:
- `machine`: MicroPython hardware interface
- `network`: WiFi connectivity
- `time` / `utime`: Time operations
- `requests`: HTTP POST requests to Firebase
- `dht`: DHT11 sensor driver
- `gc`: Garbage collection

### External APIs:
- **Firebase Realtime Database**: 
  - Endpoint: `https://air-quality-80aa6-default-rtdb.firebaseio.com/air_quality_measure.json`

---

## 🚀 How to Use

### 1. Hardware Setup
- Connect DHT11 sensor to GPIO13
- Connect MQ-135 air quality sensor to GPIO36 (ADC0)
- Connect Buzzer to GPIO14
- Connect I2C LCD (PCF8574 address 0x27) to GPIO4 (SDA) and GPIO5 (SCL)

### 2. Configuration
- Update WiFi credentials in `connection.py` (SSID and password)
- Verify Firebase endpoint URL in `fire_test.py`
- Adjust alert thresholds in `Humidity.py` if needed

### 3. Upload and Run
- Upload all Python files to microcontroller
- Execute `fire_test.py`
- Monitor console for connection and data upload status
- Data will appear on LCD display
- Cloud data stored in Firebase

### 4. Monitoring
- Check Firebase console for real-time data
- LCD displays current temperature and air quality
- Console prints detailed sensor readings
- Buzzer alerts on abnormal conditions

---

## ⚙️ Configuration Parameters

| Parameter | Value | Location |
|-----------|-------|----------|
| DHT Sensor Pin | GPIO13 | Humidity.py |
| Buzzer Pin | GPIO14 | Humidity.py |
| ADC Sensor Pin | GPIO0/36 | air_quality.py |
| I2C SCL | GPIO5 | fire_test.py |
| I2C SDA | GPIO4 | fire_test.py |
| I2C Address | 0x27 | fire_test.py |
| LCD Rows | 2 | fire_test.py |
| LCD Columns | 16 | fire_test.py |
| WiFi SSID | "suman" | connection.py |
| WiFi Password | "12345678" | connection.py |
| Data Upload Interval | 2 seconds | fire_test.py |

---

## 🚨 Alert Thresholds

| Condition | Threshold | Action |
|-----------|-----------|--------|
| High Temperature | > 30°C | Buzzer ON |
| High Humidity | > 90% | Buzzer ON |
| Low Humidity | < 30% | Buzzer ON |
| Normal Conditions | All OK | Buzzer OFF |

---

## 🐛 Troubleshooting

### WiFi Connection Issues
- Verify SSID and password in `connection.py`
- Check microcontroller is in range of WiFi network
- Monitor console output for connection status

### Sensor Reading Issues
- Verify pin connections match configuration
- Ensure sensors are powered correctly
- Check for loose connections

### Firebase Upload Failures
- Verify internet connection
- Check Firebase endpoint URL
- Ensure database has write permissions

### LCD Display Issues
- Verify I2C address (default 0x27)
- Check SCL/SDA pin connections
- Confirm I2C frequency is set to 10kHz

---

## 📝 License

This project is for IoT environmental monitoring and educational purposes.

---

## 👤 Author

Created by: Suman-Gayen

---

**Last Updated**: March 19, 2026