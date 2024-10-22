import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('3-1-mekong-water-level-future-data-predicted.csv')

# Preprocess the data
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

# Plot water level time series
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['water level (cm)'], label='Water Level (cm)', color='b')

# Plot prediction time series
plt.plot(df.index, df['prediction'], label='Prediction', color='r', linestyle='--')

# Add titles and labels
plt.title('Water Level and Flash Flood Prediction')
plt.xlabel('Datetime')
plt.ylabel('Water Level (cm) / Prediction')
plt.legend()

# Show plot
plt.show()