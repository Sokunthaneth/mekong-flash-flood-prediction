# Generate sampling dataset with the following criteria:
# - Water level rises from 01/07/2024 to a maximum of 550 cm by 31/10/2024.
# - Then begins to drop to a minimum of around 150 cm by the end of the year.
# - Two flash flood events:
#     - One on 15/08/2024 with water level at 1000 cm, start to increase 2 days before and ease back 5 days after.
#     - Another on 21/10/2024 with water level at 1200 cm, start to increase 5 days before and ease back 7 days after.


import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Initialize water levels again based on the new logic
water_levels = []
start_date = datetime(2024, 6, 1, 0, 0)
end_date = datetime(2024, 12, 31, 23, 59)
time_interval = timedelta(minutes=10)

start_rise_date = datetime(2024, 7, 1)
peak_date = datetime(2024, 10, 31)
end_date = datetime(2024, 12, 31)

# Calculate the number of days for rising and falling periods
days_to_peak = (peak_date - start_rise_date).days
days_to_end = (end_date - peak_date).days

# Flash flood event details
flash_flood_1_date = datetime(2024, 8, 15)
flash_flood_2_date = datetime(2024, 10, 21)

# Rapid rise and ease back period for flash flood 1
rapid_rise_start_date_1 = flash_flood_1_date - timedelta(days=2)
ease_back_end_date_1 = flash_flood_1_date + timedelta(days=5)

# Rapid rise and ease back period for flash flood 2
rapid_rise_start_date_2 = flash_flood_2_date - timedelta(days=5)
ease_back_end_date_2 = flash_flood_2_date + timedelta(days=7)

# Create a list of dates with the given time interval
timestamps = []
current_time = start_date
while current_time <= end_date:
    timestamps.append(current_time)
    current_time += time_interval

for timestamp in timestamps:
    if timestamp == flash_flood_1_date:
        base_level = 1000  # Flash flood event 1
    elif timestamp == flash_flood_2_date:
        base_level = 1200  # Flash flood event 2
    elif rapid_rise_start_date_1 <= timestamp < flash_flood_1_date:
        # Rapid rise to 1000 cm over 2 days
        base_level = 100 + (timestamp - rapid_rise_start_date_1).days * \
            (1000 - 100) / 2
    elif flash_flood_1_date < timestamp <= ease_back_end_date_1:
        # Ease back to normal over 5 days
        base_level = 1000 - (timestamp - flash_flood_1_date).days * \
            (1000 - 550) / 5
    elif rapid_rise_start_date_2 <= timestamp < flash_flood_2_date:
        # Rapid rise to 1200 cm over 5 days
        base_level = 100 + (timestamp - rapid_rise_start_date_2).days * \
            (1200 - 100) / 5
    elif flash_flood_2_date < timestamp <= ease_back_end_date_2:
        # Ease back to normal over 7 days
        base_level = 1200 - (timestamp - flash_flood_2_date).days * \
            (1200 - 550) / 7
    elif timestamp >= start_rise_date and timestamp <= peak_date:
        # Linear increase in water level from 100 cm to 550 cm
        base_level = 100 + (timestamp - start_rise_date).days * \
            (550 - 100) / days_to_peak
    elif timestamp > peak_date:
        # Linear decrease in water level from 550 cm to 150 cm by the end of the year
        base_level = 550 - (timestamp - peak_date).days * \
            (550 - 150) / days_to_end
    else:
        # Before the start rise date, keep it around a baseline value (e.g., 100 cm)
        base_level = 100

    # Add random fluctuation to simulate natural variability except for flash flood events
    if timestamp != flash_flood_1_date and timestamp != flash_flood_2_date:
        fluctuation = np.random.normal(0, 5)
        # Ensure water level is not negative
        water_level = max(0, base_level + fluctuation)
    else:
        water_level = base_level  # For flash flood events, use the exact level

    water_levels.append(round(water_level, 2))

# Create the final DataFrame with all conditions
df_flash_floods = pd.DataFrame({
    'date': [ts.strftime('%d/%m/%Y') for ts in timestamps],
    'time': [ts.strftime('%H:%M:%S') for ts in timestamps],
    'water level (cm)': water_levels
})

# Save the final dataset with flash flood events to a CSV file
csv_file_path_flash_floods = 'mekong_water_level_forecast_2024_flash_floods.csv'
df_flash_floods.to_csv(csv_file_path_flash_floods, index=False)
