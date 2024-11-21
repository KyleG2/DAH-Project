# Data Acquisition and Handling Project

This is a collection of all the code used during the Data Acquisition and Handling Project.

## Microcontroller Code

### .ino Files
- The `.ino` codes are for programming the microcontroller and are uploaded after the microcontroller is put into bootloader mode.

### WiFi_Code.ino
- This code was made by Anne Barela for Adafruit Industries.
- It reads the **DHT22 sensor** and makes the data accessible through a web server so it can be read using `urllib.request` in Python.
- The only alteration needed for the code to work in this case was changing the name and password of the WiFi network.

### LED_Code.ino
- This code is designed to measure the temperature from the **DHT22 sensor** using the **ESP8266 microcontroller**.
- If the temperature is above or below some specified thresholds, the microcontroller turns on one of two LEDs connected to its GPIO pins.
- **Potential Use**:
  - Instead of LEDs, a fan or heater could be used to cool or heat the system to keep the temperature within the threshold values, automatically maintaining an optimal temperature.
  - A similar system could be implemented for maintaining optimal humidity.

## Python Code

### Get_Readings_and_Write.py
- **Purpose**:
  - Reads the **DHT22 sensor values** from the web server intermittently and writes these values to a `.txt` file.
  - It also prints the values to the console so you can review whether the data is reasonable as it's being collected.

### Animated_Plot.py
- **Purpose**:
  - Periodically retrieves sensor data from the web server but does not write the data to a file.
  - Instead, it updates an animated plot of **temperature vs. humidity** in real-time by adding new data points each time data is retrieved from the web server.
- **Use Case**:
  - This was used to observe what values the sensor read under heating from a hairdryer.

### Calibration_Analysis.py
- **Purpose**:
  - Used to analyze the relationship between the readings from the **DHT22 sensor** and a **Lascar Electronics data logger**.
- **Features**:
  - Plots **temperature vs. time** and **humidity vs. time** for both devices.
  - Matches the data points between the devices in time, ensuring each sensor data point has a corresponding data logger data point.
  - Creates scatter plots:
    - **Data Logger Temperature vs. Sensor Temperature**
    - **Data Logger Humidity vs. Sensor Humidity**
  - Performs a linear fit to the scatter plots and overlays the fitted line on the graphs.
