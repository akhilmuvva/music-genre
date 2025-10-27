Place the trained model files here:

- knn_model.pkl
- minmax_scaler.pkl
- label_encoder.pkl

The `predictor.py` expects these files to be present in this directory. If your model files have different names, either rename them accordingly or update `predictor.py` to point to the correct filenames.

If model files are large, consider storing them outside version control and keeping only a download/install step in this README or using an environment variable to point to an external path.
