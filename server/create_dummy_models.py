import os
import pickle
import numpy as np

class DummyModel:
    def predict(self, X):
        # Return a single label index
        return np.array([0])

class DummyScaler:
    def transform(self, X):
        # If X is a pandas DataFrame, return its values; otherwise return as-is
        try:
            return X.values
        except Exception:
            return X

class DummyLabelEncoder:
    def inverse_transform(self, y):
        # Map any label index to 'unknown'
        return np.array(['unknown' for _ in y])

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

with open(os.path.join(MODEL_DIR, 'knn_model.pkl'), 'wb') as f:
    pickle.dump(DummyModel(), f)

with open(os.path.join(MODEL_DIR, 'minmax_scaler.pkl'), 'wb') as f:
    pickle.dump(DummyScaler(), f)

with open(os.path.join(MODEL_DIR, 'label_encoder.pkl'), 'wb') as f:
    pickle.dump(DummyLabelEncoder(), f)

print('Dummy model files created at', MODEL_DIR)
