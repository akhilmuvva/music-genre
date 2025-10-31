"""
WSGI config for music_genre_classifier project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_genre_classifier.settings')

# Optional: download model files at startup when running in an environment
# where models are stored in S3. This ensures the `/app/models` directory
# contains the expected pickles before Django boots.
def _maybe_download_models_from_s3():
	try:
		model_strategy = os.environ.get('MODEL_STRATEGY', '').lower()
		if model_strategy != 's3':
			return

		# Import boto3 lazily (added to requirements.txt) so local dev without
		# boto3 keeps working until MODEL_STRATEGY=s3 is used.
		import boto3
		from botocore.exceptions import BotoCoreError, NoCredentialsError

		bucket = os.environ.get('S3_BUCKET')
		prefix = os.environ.get('S3_PREFIX', '').rstrip('/')
		region = os.environ.get('S3_REGION') or None
		if not bucket:
			# Missing config; don't block startup — models will be created as dummy later.
			return

		model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
		os.makedirs(model_dir, exist_ok=True)

		s3 = boto3.client('s3', region_name=region,
						  aws_access_key_id=os.environ.get('S3_ACCESS_KEY_ID'),
						  aws_secret_access_key=os.environ.get('S3_SECRET_ACCESS_KEY'))

		expected = ['knn_model.pkl', 'minmax_scaler.pkl', 'label_encoder.pkl']
		for name in expected:
			key = f"{prefix}/{name}" if prefix else name
			dest = os.path.join(model_dir, name)
			if os.path.exists(dest):
				continue
			try:
				with open(dest, 'wb') as fh:
					s3.download_fileobj(bucket, key, fh)
				print(f"Downloaded model {name} from s3://{bucket}/{key}")
			except (BotoCoreError, NoCredentialsError) as e:
				# Log and continue; application can still start with dummy models.
				print(f"Warning: failed to download {key} from S3: {e}")
			except Exception as e:
				print(f"Warning: unexpected error downloading {key}: {e}")
	except Exception as e:
		# Never let model-download code crash the whole WSGI initialization.
		print(f"Model download check failed: {e}")


# Attempt model download before creating the WSGI application
_maybe_download_models_from_s3()

application = get_wsgi_application()
