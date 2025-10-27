import os
import pickle
import io
import wave
from pathlib import Path

import numpy as np
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile


class PredictAPITest(TestCase):
	def setUp(self):
		# Ensure model dir exists and create dummy model files the predictor expects
		project_root = Path(__file__).resolve().parents[1]
		model_dir = project_root / 'models'
		os.makedirs(model_dir, exist_ok=True)

		class DummyModel:
			def predict(self, X):
				return np.array([0])

		class DummyScaler:
			def transform(self, X):
				try:
					return X.values
				except Exception:
					return X

		class DummyLabelEncoder:
			def inverse_transform(self, y):
				return np.array(['test-genre' for _ in y])

		with open(model_dir / 'knn_model.pkl', 'wb') as f:
			pickle.dump(DummyModel(), f)
		with open(model_dir / 'minmax_scaler.pkl', 'wb') as f:
			pickle.dump(DummyScaler(), f)
		with open(model_dir / 'label_encoder.pkl', 'wb') as f:
			pickle.dump(DummyLabelEncoder(), f)

	def test_predict_api_returns_genre(self):
		# generate a short WAV file in memory (mono, 16-bit PCM)
		sr = 22050
		duration = 0.5
		t = np.linspace(0, duration, int(sr * duration), False)
		tone = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
		pcm = (tone * 32767).astype(np.int16)

		buf = io.BytesIO()
		with wave.open(buf, 'wb') as wf:
			wf.setnchannels(1)
			wf.setsampwidth(2)
			wf.setframerate(sr)
			wf.writeframes(pcm.tobytes())
		buf.seek(0)

		uploaded = SimpleUploadedFile('test.wav', buf.read(), content_type='audio/wav')

		client = Client()
		resp = client.post('/api/predict', {'file': uploaded})
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		self.assertIn('genre', data)
