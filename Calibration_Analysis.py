import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import linregress

# Function to extract data from the sensor log text file
def extract_sensor_log_data(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Remove any extra whitespace and split the line into parts by commas
            parts = line.strip().split(',')

            # Extract the timestamp string (first part of the line)
            time_str = parts[0]

            # Extract the temperature string:
            # Split by ': ' to isolate the temperature value and then take the part before the unit ('F' or 'C')
            temp_str = parts[1].split(': ')[1].split(' ')[0]

            # Extract the humidity string:
            # Split by ': ' to isolate the humidity value and remove the '%' sign
            humidity_str = parts[2].split(': ')[1].replace('%', '')

            # Parse the timestamp string into a datetime object for easier manipulation
            timestamp = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

            # Convert the extracted temperature and humidity strings to floating-point numbers
            sensor_temperature = float(temp_str)
            sensor_humidity = float(humidity_str)

            # Append the parsed values (timestamp, temperature, humidity) as a tuple to the data list
            data.append((timestamp, sensor_temperature, sensor_humidity))
    
    # After reading the file, convert the list of tuples into a pandas DataFrame
    # Columns are labeled as 'Time', 'Sensor_Temperature', and 'Sensor_Humidity'
    sensor_df = pd.DataFrame(data, columns=['Time', 'Sensor_Temperature', 'Sensor_Humidity'])
    return sensor_df

# Function to extract data from the CSV files
def extract_csv_data(file_paths):
    data_frames = []
    #do for both of the file paths given
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            # Find the index where the data starts
            data_start_idx = None
            for idx, line in enumerate(lines):
                #this is the start of the line before the data is listed -the final header line
                if line.startswith('Reading,Date / Time (UTC),'):
                    data_start_idx = idx
                    break
            if data_start_idx is None:
                print(f"Data header not found in file {file_path}")
                continue
            # Read the data into a DataFrame - skip past the final header, straight to the data
            data = pd.read_csv(file_path, skiprows=data_start_idx)
            # Parse 'Date / Time (UTC)' column to datetime
            data['Date / Time (UTC)'] = pd.to_datetime(data['Date / Time (UTC)'], format='%Y/%m/%d %H:%M:%S')
            # Keep only the columns we need: Time, Temperature, Humidity
            lascar_df = data[['Date / Time (UTC)', 'Temperature (°C)', 'Humidity (%RH)']].copy()
            #Rename columns so they're more intuitive to use
            lascar_df.rename(columns={'Date / Time (UTC)': 'Time', 'Temperature (°C)': 'Lascar_Temperature', 'Humidity (%RH)': 'Lascar_Humidity'}, inplace=True)
            data_frames.append(lascar_df)
    # Concatenate all DataFrames - combine two data logger sessions into one
    if data_frames:
        combined_lascar_df = pd.concat(data_frames)
        # Sort by Time
        combined_lascar_df = combined_lascar_df.sort_values('Time')
        return combined_lascar_df
    else:
        return pd.DataFrame(columns=['Time', 'Lascar_Temperature', 'Lascar_Humidity'])

# File paths
sensor_log_file = 'sensor_log.txt'
csv_files = ['CSV-Data-Session1.csv', 'CSV-Data-Session2.csv']

# Extract data
sensor_data = extract_sensor_log_data(sensor_log_file)
lascar_data = extract_csv_data(csv_files)

# Ensure both DataFrames are sorted by 'Time'
sensor_data = sensor_data.sort_values('Time')
lascar_data = lascar_data.sort_values('Time')

# Find overall min and max times for x-axis alignment
min_time = min(sensor_data['Time'].min(), lascar_data['Time'].min())
max_time = max(sensor_data['Time'].max(), lascar_data['Time'].max())

# Create subplots - so there's one on top of the other.
fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Plot DHT22 sensor data on top subplot
axs[0].plot(sensor_data['Time'], sensor_data['Sensor_Temperature'], label='Temperature (°C)', marker='o')
axs[0].plot(sensor_data['Time'], sensor_data['Sensor_Humidity'], label='Humidity (%)', marker='o')
axs[0].set_title('DHT22 Sensor: Temperature and Humidity vs Time')
axs[0].set_ylabel('Value')
axs[0].legend()
axs[0].grid()

# Plot Lascar Electronics data logger data on bottom subplot
axs[1].plot(lascar_data['Time'], lascar_data['Lascar_Temperature'], label='Temperature (°C)', marker='o')
axs[1].plot(lascar_data['Time'], lascar_data['Lascar_Humidity'], label='Humidity (%)', marker='o')
axs[1].set_title('Lascar Electronics Data Logger: Temperature and Humidity vs Time')
axs[1].set_xlabel('Time')
axs[1].set_ylabel('Value')
axs[1].legend()
axs[1].grid()

# Set x-axis limits to align times
axs[0].set_xlim([min_time, max_time])

# Format x-axis to show only the time
time_formatter = DateFormatter('%H:%M')  # Time format: HH:MM
axs[1].xaxis.set_major_formatter(time_formatter)

# Rotate x-ticks for better readability
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# Debugging prints to ensure mask is working - ignore
#print(len(sensor_data),"length of sensor data before omitting t<2:30")

# Emit sensor data for times before 2:30 because there is no matching data logger data
# Tolerance on merge_asof deals with this anyways but it doesn't hurt to do explicitly
sensor_data = sensor_data[sensor_data['Time'].dt.time >= datetime.strptime("14:30", "%H:%M").time()]

#print(len(sensor_data),"length of sensor data after omitting t<2:30")

# Match each sensor log data point to a Lascar data point occurring at around the same time
# Use pandas merge_asof function to merge on nearest times within a tolerance
merged_data = pd.merge_asof(sensor_data, lascar_data, on='Time', direction='nearest', tolerance=pd.Timedelta('10sec'))

# Remove any rows where a match wasn't found within the tolerance
merged_data = merged_data.dropna(subset=['Lascar_Temperature', 'Lascar_Humidity'])

# Linear fitting for Temperature
slope_temp, intercept_temp, r_value_temp, p_value_temp, std_err_temp = linregress(
    merged_data['Sensor_Temperature'], merged_data['Lascar_Temperature'])

# Equation for Temperature
line_temp = slope_temp * merged_data['Sensor_Temperature'] + intercept_temp

# Plot Lascar Temperature vs Sensor Temperature with a 45-degree line (ideal fit) and fitted line
plt.figure(figsize=(8, 8))
#scatter plot the data logger vs sensor temperature values.
plt.scatter(merged_data['Sensor_Temperature'], merged_data['Lascar_Temperature'], color='black', label='Data Points')
#overplot the the linear fit and add fit m and c from fit to legend
plt.plot(merged_data['Sensor_Temperature'], line_temp, 'r-', label=f'Fit: y = {slope_temp:.2f}x + {intercept_temp:.2f}')
#overplot a line y = x so that it spans the whole dataset
plt.plot([merged_data['Sensor_Temperature'].min(), merged_data['Sensor_Temperature'].max()],
         [merged_data['Sensor_Temperature'].min(), merged_data['Sensor_Temperature'].max()],
         '--', label='Ideal (y = x)')
plt.xlabel('DHT22 Temperature (°C)')
plt.ylabel('Data Logger Temperature (°C)')
plt.title('Data Logger Temperature vs DHT22 Temperature')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Linear fitting for Humidity
slope_humid, intercept_humid, r_value_humid, p_value_humid, std_err_humid = linregress(
    merged_data['Sensor_Humidity'], merged_data['Lascar_Humidity'])

# Equation for Humidity
line_humid = slope_humid * merged_data['Sensor_Humidity'] + intercept_humid

# Plot Lascar Humidity vs Sensor Humidity with a 45-degree line (ideal fit) and fitted line
plt.figure(figsize=(8, 8))
# Scatter plot the data logger vs sensor humidity values.
plt.scatter(merged_data['Sensor_Humidity'], merged_data['Lascar_Humidity'], color='black', label='Data Points')
# Overplot the the linear fit and add fit m and c from fit to legend
plt.plot(merged_data['Sensor_Humidity'], line_humid, 'r-', label=f'Fit: y = {slope_humid:.2f}x + {intercept_humid:.2f}')
# Overplot a line y = x so that it spans the whole dataset
plt.plot([merged_data['Sensor_Humidity'].min(), merged_data['Sensor_Humidity'].max()],
         [merged_data['Sensor_Humidity'].min(), merged_data['Sensor_Humidity'].max()],
         '--', label='Ideal (y = x)')
plt.xlabel('DHT22 Humidity (%)')
plt.ylabel('Data Logger Humidity (%)')
plt.title('Data Logger Humidity vs DHT22 Humidity')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()