const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const cors = require('cors');

const app = express();
app.use(cors());

const upload = multer({ dest: path.join(__dirname, 'uploads/') });

// If you have deployed your Colab model as an HTTP endpoint, set MODEL_API_URL in env or replace below
const MODEL_API_URL = process.env.MODEL_API_URL || '';

app.post('/api/predict', upload.single('file'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

  try {
    if (MODEL_API_URL) {
      // Proxy file to remote model endpoint
      const form = new FormData();
      form.append('file', fs.createReadStream(req.file.path), req.file.originalname);

      const response = await axios.post(MODEL_API_URL, form, {
        headers: { ...form.getHeaders() },
        timeout: 120000,
      });

      // forward model response
      return res.json(response.data);
    }

    // Fallback: simple heuristic based on filename
    const names = ['Pop', 'Rock', 'Jazz', 'Hip-Hop', 'Classical', 'Electronic'];
    const pick = names[(req.file.originalname.length + req.file.size) % names.length];

    return res.json({ genre: pick, source: 'fallback' });
  } catch (err) {
    console.error(err && err.message ? err.message : err);
    return res.status(500).json({ error: 'Prediction failed', detail: err.toString() });
  } finally {
    // cleanup upload
    fs.unlink(req.file.path, () => {});
  }
});

// Serve client production build when present
const buildPath = path.join(__dirname, '..', 'build');
if (fs.existsSync(buildPath)) {
  app.use(express.static(buildPath));
  // SPA fallback
  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/api/')) return next();
    res.sendFile(path.join(buildPath, 'index.html'));
  });
}

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Server listening on ${port}`));
