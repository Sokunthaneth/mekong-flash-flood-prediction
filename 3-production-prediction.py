import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

# Load the saved model
model = load_model('flash_flood_prediction_model.h5')


# Function to preprocess the future data
def preprocess_future_data(data):
    # Combine date and time into a single datetime column
    data['datetime'] = pd.to_datetime(
        data['date'] + ' ' + data['time'], format='%d/%m/%Y %H:%M:%S')
    data.set_index('datetime', inplace=True)
    data.drop(['date', 'time'], axis=1, inplace=True)

    # Normalize the water level
    scaler = MinMaxScaler(feature_range=(0, 1))
    data['water level (cm)'] = scaler.fit_transform(data[['water level (cm)']])

    return data, scaler


# Load and preprocess the future data
future_data = pd.read_csv('mekong_water_level_future_data.csv')


future_data, _ = preprocess_future_data(future_data)


# Prepare the data for LSTM
def create_sequences(data, seq_length):
    X = []
    for i in range(len(data) - seq_length):
        X.append(data.iloc[i:i+seq_length, :-1].values)
    return np.array(X)


seq_length = 10  # Number of time steps to look back
X_future = create_sequences(future_data, seq_length)

# Make predictions
predictions = (model.predict(X_future) > 0.5).astype("int32")

# Add predictions to the future data
future_data['prediction'] = np.nan
future_data.iloc[seq_length:, future_data.columns.get_loc(
    'prediction')] = predictions.flatten()

# Save the predictions to a new CSV file
future_data.to_csv('future_data_with_predictions.csv')
