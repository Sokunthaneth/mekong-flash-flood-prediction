# Summary of Changes
# SMOTE: Applied to balance the training data.
# Class Weights: Computed and used during model training.
# Precision-Recall AUC: Calculated and printed for better evaluation of model performance on imbalanced data.

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report, precision_recall_curve, auc
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Load the training and test data
train_data = pd.read_csv('train-test-split-data/training-data.csv')
test_data = pd.read_csv('train-test-split-data/test-data.csv')

# Preprocess the data
def preprocess_data(data):
    # Combine date and time into a single datetime column
    data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'], format='%d/%m/%Y %H:%M:%S')
    data.set_index('datetime', inplace=True)
    data.drop(['date', 'time'], axis=1, inplace=True)

    # Normalize the water level
    scaler = MinMaxScaler(feature_range=(0, 1))
    data['water level (cm)'] = scaler.fit_transform(data[['water level (cm)']])

    return data, scaler

train_data, scaler = preprocess_data(train_data)
test_data, _ = preprocess_data(test_data)

# Prepare the data for LSTM
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data.iloc[i:i+seq_length, :-1].values)
        y.append(data.iloc[i+seq_length, -1])
    return np.array(X), np.array(y)

seq_length = 10  # Number of time steps to look back
X_train, y_train = create_sequences(train_data, seq_length)
X_test, y_test = create_sequences(test_data, seq_length)

# Reshape y_train and y_test to 1D arrays for SMOTE
y_train = y_train.reshape(-1)
y_test = y_test.reshape(-1)

# Ensure y_train contains binary values (0 or 1)
y_train_binary = (y_train > 0.5).astype(int)

# Apply SMOTE to balance the training data
smote = SMOTE(random_state=42)
X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_reshaped, y_train_binary)

# Reshape X_train_resampled back to 3D array
X_train_resampled = X_train_resampled.reshape(-1, seq_length, X_train.shape[2])

# Compute class weights
class_weights = compute_class_weight('balanced', classes=np.unique(y_train_resampled), y=y_train_resampled)
class_weights_dict = dict(enumerate(class_weights))

# Build the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(seq_length, X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(50))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train_resampled, y_train_resampled, epochs=20, batch_size=32, validation_split=0.2, class_weight=class_weights_dict)

# Evaluate the model
y_pred = (model.predict(X_test) > 0.5).astype("int32")
y_test_binary = (y_test > 0.5).astype("int32")
print(classification_report(y_test_binary, y_pred))

# Calculate Precision-Recall AUC
precision, recall, _ = precision_recall_curve(y_test_binary, y_pred)
pr_auc = auc(recall, precision)
print(f'Precision-Recall AUC: {pr_auc}')

# Save the model
model.save('flash_flood_prediction_model.h5')