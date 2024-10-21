import pandas as pd
import matplotlib.pyplot as plt

# Load the data
csv_file_path = 'mekong_water_level_forecast_2024_flash_floods.csv'
df = pd.read_csv(csv_file_path)

# Combine date and time into a single datetime column
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%d/%m/%Y %H:%M:%S')

# Set the datetime column as the index
df.set_index('datetime', inplace=True)

# Plot the time series
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['water level (cm)'], label='Water Level (cm)')
plt.xlabel('Date and Time')
plt.ylabel('Water Level (cm)')
plt.title('Mekong Water Level Forecast 2024 with Flash Floods')
plt.legend()
plt.grid(True)
plt.show()