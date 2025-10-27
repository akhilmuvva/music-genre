import librosa
import pandas as pd
import numpy as np
from sklearn import preprocessing
import warnings
import pickle

warnings.filterwarnings('ignore') # Ignore warnings for cleaner output

# Define the feature columns based on your training data X
# Assuming X had these columns during training
feature_cols = ['length', 'chroma_stft_mean', 'chroma_stft_var', 'rms_mean', 'rms_var', 'spectral_centroid_mean',
                'spectral_centroid_var', 'spectral_bandwidth_mean', 'spectral_bandwidth_var', 'rolloff_mean',
                'rolloff_var', 'zero_crossing_rate_mean', 'zero_crossing_rate_var', 'harmony_mean', 'harmony_var',
                'perceptr_mean', 'perceptr_var', 'tempo', 'mfcc1_mean', 'mfcc1_var', 'mfcc2_mean', 'mfcc2_var',
                'mfcc3_mean', 'mfcc3_var', 'mfcc4_mean', 'mfcc4_var', 'mfcc5_mean', 'mfcc5_var', 'mfcc6_mean',
                'mfcc6_var', 'mfcc7_mean', 'mfcc7_var', 'mfcc8_mean', 'mfcc8_var', 'mfcc9_mean', 'mfcc9_var',
                'mfcc10_mean', 'mfcc10_var', 'mfcc11_mean', 'mfcc11_var', 'mfcc12_mean', 'mfcc12_var', 'mfcc13_mean',
                'mfcc13_var', 'mfcc14_mean', 'mfcc14_var', 'mfcc15_mean', 'mfcc15_var', 'mfcc16_mean', 'mfcc16_var',
                'mfcc17_mean', 'mfcc17_var', 'mfcc18_mean', 'mfcc18_var', 'mfcc19_mean', 'mfcc19_var', 'mfcc20_mean',
                'mfcc20_var']


def extract_features(audio_path):
    """Extracts features from an audio file.

    Args:
        audio_path: Path to the audio file.

    Returns:
        A pandas DataFrame containing the extracted features.
    """
    y, sr = librosa.load(audio_path, sr=None)

    features = {}

    # Extract chroma_stft features
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    features['chroma_stft_mean'] = np.mean(chroma_stft)
    features['chroma_stft_var'] = np.var(chroma_stft)

    # Extract rms features
    rms = librosa.feature.rms(y=y)
    features['rms_mean'] = np.mean(rms)
    features['rms_var'] = np.var(rms)

    # Extract spectral_centroid features
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    features['spectral_centroid_mean'] = np.mean(spectral_centroid)
    features['spectral_centroid_var'] = np.var(spectral_centroid)

    # Extract spectral_bandwidth features
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
    features['spectral_bandwidth_var'] = np.var(spectral_bandwidth)

    # Extract rolloff features
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    features['rolloff_mean'] = np.mean(rolloff)
    features['rolloff_var'] = np.var(rolloff)

    # Extract zero_crossing_rate features
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y)
    features['zero_crossing_rate_mean'] = np.mean(zero_crossing_rate)
    features['zero_crossing_rate_var'] = np.var(zero_crossing_rate)

    # Extract harmony and perceptr features
    harmony, perceptr = librosa.effects.hpss(y)
    features['harmony_mean'] = np.mean(harmony)
    features['harmony_var'] = np.var(harmony)
    features['perceptr_mean'] = np.mean(perceptr)
    features['perceptr_var'] = np.var(perceptr)

    # Extract mfcc features
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    for i in range(20):
        features[f'mfcc{i+1}_mean'] = np.mean(mfcc[i])
        features[f'mfcc{i+1}_var'] = np.var(mfcc[i])

    # Extract tempo feature
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    features['tempo'] = tempo

    # Add length feature (assuming a fixed length or calculating it if needed)
    features['length'] = len(y) # Or use a fixed value if appropriate

    # Convert features to a DataFrame
    features_df = pd.DataFrame([features])

    return features_df


def predict_genre(audio_path):
    """Predicts the genre of an audio file using a pre-trained model.

    Args:
        audio_path: Path to the audio file.

    Returns:
        The predicted genre name as a string, or an error message.
    """
    try:
        # Load the saved objects
        with open('knn_model.pkl', 'rb') as f:
            loaded_model = pickle.load(f)
        with open('minmax_scaler.pkl', 'rb') as f:
            loaded_scaler = pickle.load(f)
        with open('label_encoder.pkl', 'rb') as f:
            loaded_label_encoder = pickle.load(f)

        # Extract features
        extracted_features_df = extract_features(audio_path)

        # Ensure the order of columns matches the training data
        extracted_features_df = extracted_features_df[feature_cols]

        # Scale the extracted features
        extracted_features_scaled = loaded_scaler.transform(extracted_features_df)
        extracted_features_df_scaled = pd.DataFrame(extracted_features_scaled, columns=feature_cols)

        # Predict the genre
        predicted_label = loaded_model.predict(extracted_features_df_scaled)

        # Map the predicted label back to the original genre name
        predicted_genre = loaded_label_encoder.inverse_transform(predicted_label)

        return predicted_genre[0]

    except FileNotFoundError:
        return "Error: Model, scaler, or label encoder files not found."
    except Exception as e:
        return f"Error during prediction: {e}"
