#Script for getting readings and writing them to a file (and printing them)


import urllib.request  # Module for fetching URLs (for accessing the sensor's web server)
import re              # Module for regular expressions (for parsing the HTML data)
import time            # Module for handling time-related functions (for timestamps and delays)

def fetch_sensor_data(url):
    """
    Fetch the raw HTML data from the sensor's web server.

    Args:
        url (str): The URL of the sensor's web server.

    Returns:
        str: The HTML content retrieved from the server, or None if an error occurs.
    """
    try:
        # Open the URL and read the response
        with urllib.request.urlopen(url) as response:
            # Read the data and decode it from bytes to a UTF-8 string
            data = response.read().decode('utf-8')
            return data
    except Exception as e:
        # Print an error message if something goes wrong during the request
        print(f"Error fetching data from {url}: {e}")
        return None

def parse_sensor_data_temp(temp_html_data):
    """
    Parse the temperature data from the HTML content.

    Args:
        html_data (str): The HTML content containing the sensor data.

    Returns:
        float: A float - the temperature in Fahrenheit,
               or None if parsing fails.
    """
    try:
        # Define regular expression patterns to find temperature values
        temp_pattern = r"Temperature: ([\d\.]+) F"

        # Search the HTML data for the temperature pattern
        temp_match = re.search(temp_pattern, temp_html_data)

        if temp_match:
            # Extract the temperature value from the regex match and convert to float
            temperature_f = float(temp_match.group(1))
           
            return temperature_f
        else:
            # If the pattern is not found, print a warning message
            print("Failed to parse sensor temperature data from HTML content.")
            return None
    except Exception as e:
        # Print an error message if something goes wrong during parsing
        print(f"Error parsing sensor temperature data: {e}")
        return None
       
def parse_sensor_data_hmdt(hmdt_html_data):
    """
    Parse the humidity data from the HTML content.

    Args:
        html_data (str): The HTML content containing the sensor data.

    Returns:
        float: A float - the humidity percentage,
               or None if parsing fails.
    """
    try:
        # Define regular expression patterns to find humidity values
        humidity_pattern = r"Humidity: ([\d\.]+)%"

        # Search the HTML data for the humidity pattern
        humidity_match = re.search(humidity_pattern, hmdt_html_data)

        if humidity_match:
            # Extract the humidity value from the regex match and convert to float
            humidity = float(humidity_match.group(1))
            return humidity
        else:
            # If the pattern is not found, print a warning message
            print("Failed to parse sensor humidity data from HTML content.")
            return None
    except Exception as e:
        # Print an error message if something goes wrong during parsing
        print(f"Error parsing sensor humidity data: {e}")
        return None

def fahrenheit_to_celsius(temp_f):
    """
    Convert a temperature from Fahrenheit to Celsius.

    Args:
        temp_f (float): Temperature in degrees Fahrenheit.

    Returns:
        float: Temperature converted to degrees Celsius.
    """
    # Apply the Fahrenheit to Celsius conversion formula
    temp_c = (temp_f - 32) * 5.0 / 9.0
    return temp_c

#this writes the data to a file
def log_data(temperature_c, humidity):
    """
    Log the temperature and humidity data with a timestamp.

    Args:
        temperature_c (float): Temperature in degrees Celsius.
        humidity (float): Relative humidity in percentage.
    """
    # Get the current time formatted as a human-readable string
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Create a log entry string with the timestamp, temperature, and humidity
    log_entry = f"{timestamp}, Temperature: {temperature_c:.2f} °C, Humidity: {humidity:.2f}%"
    # Print the log entry to the console
    print(log_entry)
    # Open the log file in append mode and write the log entry
    with open("sensor_log.txt", "a") as file:
        file.write(log_entry + "\n")

def get_readings(temp_url,hmdt_url):
    """
    Fetch and parse sensor data from the web server, and convert the temperature to Celsius.

    Args:
        url (str): The URL of the sensor's web server.

    Returns:
        tuple: A tuple containing the temperature in Celsius and the humidity percentage,
               or (None, None) if data retrieval fails.
    """
    # Fetch the raw HTML data from the sensor's web server
    temp_html_data = fetch_sensor_data(temp_url)
    hmdt_html_data = fetch_sensor_data(hmdt_url)
    if temp_html_data and hmdt_html_data:
        # Parse the temperature and humidity values from the HTML data
        temp_f = parse_sensor_data_temp(temp_html_data)
        humidity = parse_sensor_data_hmdt(hmdt_html_data)
        if temp_f is not None and humidity is not None:
            # Convert the temperature from Fahrenheit to Celsius
            temp_c = fahrenheit_to_celsius(temp_f)
            return temp_c, humidity
    # Return None values if data fetching or parsing failed
    return None, None

def main():
    """
    Main function to periodically fetch and log sensor data.
    """
    # Define the URL of the sensor's web server
    sensor_url_temp = "http://192.168.0.5/temp"
    sensor_url_hmdt = "http://192.168.0.5/humidity"

    # Set the interval at which to update/read the sensor data (in seconds)
    UPDATE_INTERVAL = 300

    # Start an infinite loop to continuously read and log sensor data
    while True:
        # Get the temperature and humidity readings from the sensor
        temperature, humidity = get_readings(sensor_url_temp,sensor_url_hmdt)
        if temperature is not None and humidity is not None:
            # If readings are valid, log the data
            log_data(temperature, humidity)
        else:
            # If readings are invalid, print an error message
            print("No data received from sensor.")
        # Wait for the specified update interval before reading the data again
        time.sleep(UPDATE_INTERVAL)

# This ensures that the main function runs when the script is executed
if __name__ == "__main__":
    main()