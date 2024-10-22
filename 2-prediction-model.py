import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report
from sklearn.utils import class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import joblib

# Load the training and test data
train_data = pd.read_csv('train-test-split-data/training-data.csv')
test_data = pd.read_csv('train-test-split-data/test-data.csv')


# Preprocess the data
def preprocess_data(data):
    # Combine date and time into a single datetime column
    data['datetime'] = pd.to_datetime(
        data['date'] + ' ' + data['time'], format='%d/%m/%Y %H:%M:%S')
    data.set_index('datetime', inplace=True)
    data.drop(['date', 'time'], axis=1, inplace=True)

    # Normalize the water level
    scaler = MinMaxScaler(feature_range=(0, 1))
    data['water level (cm)'] = scaler.fit_transform(data[['water level (cm)']])

    # Save the scaler for future use
    joblib.dump(scaler, 'scaler.joblib')

    return data, scaler


train_data, scaler = preprocess_data(train_data)
test_data, _ = preprocess_data(test_data)


# Prepare data for LSTM
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data.iloc[i:i+seq_length]['water level (cm)'].values)
        y.append(data.iloc[i+seq_length]['flash flood'])
    return np.array(X), np.array(y)


seq_length = 10  # Number of time steps to look back
X_train, y_train = create_sequences(train_data, seq_length)
X_test, y_test = create_sequences(test_data, seq_length)

# Build the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True,
          input_shape=(seq_length, 1)))
model.add(Dropout(0.2))
model.add(LSTM(50))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=20,
                    batch_size=32, validation_split=0.2)

# Evaluate the model
y_pred = (model.predict(X_test) > 0.5).astype("int32")
y_test_binary = (y_test > 0.5).astype("int32")
print(classification_report(y_test_binary, y_pred))

# Save the model
model.save('flash_flood_prediction_model.h5')
