#Script for animated plot

import urllib.request
import re
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Global variables to store the IP address and update interval
SENSOR_URL = "http://192.168.0.5/"
temp_url = "http://192.168.0.5/temp"      #read sensor readings from these urls
hmdt_url = "http://192.168.0.5/humidity"


UPDATE_INTERVAL = 4000  # Update interval in milliseconds

# Data lists to store temperature and humidity values for plotting
temperatures = []
humidities = []

def fetch_sensor_data(url):
    """
    Fetch raw HTML data from the sensor's web server.
   
    Args:
        url (str): The URL of the sensor's web server.
       
    Returns:
        str: HTML content from the server, or None if an error occurs.
    """
    try:
        with urllib.request.urlopen(url) as response: #Send HTTP request to url
            #This reads the entire content of the response as a sequence of bytes.    
            #Since the response.read() returns a byte object, decode('utf-8') converts it into a string
            data = response.read().decode('utf-8')
            return data
    #error handling
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

#parse => break down data for easier management
def parse_sensor_data_temp(temp_html_data):
    """
    Parse the temperature and humidity data from the HTML content.

    Args:
        html_data (str): The HTML content containing the sensor data.

    Returns:
        tuple: A tuple containing the temperature in Fahrenheit and the humidity percentage,
               or (None, None) if parsing fails.
    """
    try:
        # Define regular expression patterns to find temperature and humidity values
        #r denotes raw string => regex syntax will work
        #\d: Matches any digit (0-9)
        #\.: Matches a literal period (.), allowing for decimal numbers.
        #+ allows multiple digits/ decimal points.
        # F is just fahrenheit after the temperature value
        temp_pattern = r"Temperature: ([\d\.]+) F"

        # Search the HTML data for the temperature pattern
        temp_match = re.search(temp_pattern, temp_html_data)

        if temp_match:
            # Extract the temperature value from the regex match and convert to float
            temperature_f = float(temp_match.group(1))
           
            return temperature_f
        else:
            # If the patterns are not found, print a warning message
            print("Failed to parse sensor temperature data from HTML content.")
            return None
    #error handling
    except Exception as e:
        # Print an error message if something goes wrong during parsing
        print(f"Error parsing sensor temperature data: {e}")
        return None
       
def parse_sensor_data_hmdt(hmdt_html_data):
    """
    Parse the temperature and humidity data from the HTML content.

    Args:
        html_data (str): The HTML content containing the sensor data.

    Returns:
        tuple: A tuple containing the temperature in Fahrenheit and the humidity percentage,
               or (None, None) if parsing fails.
    """
    try:
        # Define regular expression patterns to find temperature and humidity values
        humidity_pattern = r"Humidity: ([\d\.]+)%"

        # Search the HTML data for the humidity pattern
        humidity_match = re.search(humidity_pattern, hmdt_html_data)

        if humidity_match:
            # Extract the humidity value from the regex match and convert to float
            humidity = float(humidity_match.group(1))
            return humidity
        else:
            # If the patterns are not found, print a warning message
            print("Failed to parse sensor humidity data from HTML content.")
            return None
    except Exception as e:
        # Print an error message if something goes wrong during parsing
        print(f"Error parsing sensor humidity data: {e}")
        return None

def fahrenheit_to_celsius(temp_f):
    """
    Convert Fahrenheit to Celsius.
   
    Args:
        temp_f (float): Temperature in Fahrenheit.
       
    Returns:
        float: Temperature in Celsius.
    """
    return (temp_f - 32) * 5.0 / 9.0

def update_plot(frame):
    """
    Update function for the animated plot.
   
    Args:
        frame: Frame number (not used here but required by FuncAnimation).
       
    Returns:
        List of plot elements that have changed (required by FuncAnimation).
    """
   # Fetch the raw HTML data from the sensor's web server
    temp_html_data = fetch_sensor_data(temp_url)
    hmdt_html_data = fetch_sensor_data(hmdt_url)
    
    #if both the temp and humidity variable values aren't None, False, 0 or empty
    if temp_html_data and hmdt_html_data:
        # Parse the temperature and humidity values from the HTML data
        temp_f = parse_sensor_data_temp(temp_html_data)
        humidity = parse_sensor_data_hmdt(hmdt_html_data)
       
        
        #if both the temp and humidity aren't None
        if temp_f is not None and humidity is not None:
            # Convert the temperature from Fahrenheit to Celsius
            temp_c = fahrenheit_to_celsius(temp_f)

            # Append data to lists
            temperatures.append(temp_c)
            humidities.append(humidity)
           
            # Limit data lists to the last 100 points for better performance
            if len(temperatures) > 200:
                temperatures.pop(0)
                humidities.pop(0)
           
            # Clear and update the plot
            plt.cla()  # Clear the axes for the new plot
            plt.plot(temperatures, humidities, color='b', marker='o', linestyle='-')
            plt.xlabel("Temperature (°C)")
            plt.ylabel("Humidity (%)")
            plt.title("Real-Time Temperature vs. Humidity")
            plt.grid(True) #plot a grid to make value comparison easier.
           
            # Return the line object for FuncAnimation to re-render
            return plt.gca().lines
    #handles the case of temp or humidity data before parsing being falsy
    else:
        print("No data received from sensor.")
        return []

# Set up the figure and axis for Matplotlib
fig, ax = plt.subplots()
ax.set_xlim(0, 100)  # Initial x-axis limit; can be updated dynamically if needed
ax.set_ylim(0, 100)  # Initial y-axis limit; can be updated dynamically if needed

# Set up the animated plot
ani = FuncAnimation(fig, update_plot, interval=UPDATE_INTERVAL)

# Display the plot
plt.show()