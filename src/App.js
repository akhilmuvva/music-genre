import React, { useCallback, useState, useRef } from 'react';
import axios from 'axios';

const ACCEPTED = ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/wave'];

function bytesToMB(bytes) {
  return (bytes / (1024 * 1024)).toFixed(2);
}

export default function App() {
  const API_URL = process.env.NODE_ENV === 'development' ? 'http://localhost:8000/api/predict' : '/api/predict';
  const API_KEY = process.env.REACT_APP_API_TOKEN || '';
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [genre, setGenre] = useState('');
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const audioRef = useRef(null);

  const validateAndSet = useCallback((f) => {
    setError('');
    setGenre('');
    if (!f) return;
    if (!ACCEPTED.includes(f.type)) {
      setError('Invalid file type. Only MP3 and WAV are allowed.');
      return;
    }
    if (f.size > 20 * 1024 * 1024) {
      setError('File too large. Max 20 MB allowed.');
      return;
    }
    setFile(f);
    // send to backend for prediction
    (async () => {
      setLoading(true);
      setGenre('');
      try {
        const form = new FormData();
        form.append('file', f, f.name);
  const headers = { 'Content-Type': 'multipart/form-data' };
  if (API_KEY) headers['X-API-KEY'] = API_KEY;
  const resp = await axios.post(API_URL, form, { headers, timeout: 120000 });
        if (resp.data && resp.data.genre) {
          setGenre(resp.data.genre + (resp.data.source ? ` (${resp.data.source})` : ''));
        } else {
          // fallback deterministic
          const names = ['Pop', 'Rock', 'Jazz', 'Hip-Hop', 'Classical', 'Electronic'];
          const pick = names[(f.name.length + f.size) % names.length];
          setGenre(pick + ' (fallback)');
        }
      } catch (err) {
        console.error(err);
        setError('Prediction failed. See console for details.');
        const names = ['Pop', 'Rock', 'Jazz', 'Hip-Hop', 'Classical', 'Electronic'];
        const pick = names[(f.name.length + f.size) % names.length];
        setGenre(pick + ' (fallback)');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length) {
      validateAndSet(dt.files[0]);
    }
  }, [validateAndSet]);

  const onFileChange = useCallback((e) => {
    const f = e.target.files && e.target.files[0];
    validateAndSet(f);
  }, [validateAndSet]);

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const onDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const removeFile = () => {
    setFile(null);
    setGenre('');
    setError('');
    if (audioRef.current) audioRef.current.pause();
  };

  return (
    <div className="page">
      <div className="card">
        <div className="note note-left">♪</div>
        <div className="note note-right">♪</div>

        <div className="logo">♪</div>
        <h1 className="titleGradient">Music Genre Classifier</h1>
        <p className="subtitle">Upload your music and discover its genre</p>

        <div className={`uploadWrap ${dragActive ? 'active' : ''}`} onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave}>
          <div className="innerDashed">
            <input
              id="fileInput"
              type="file"
              accept="audio/*"
              onChange={onFileChange}
              style={{ display: 'none' }}
            />

            <label htmlFor="fileInput" className="chooseBtn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="uploadSvg">
                <path d="M12 3v12" stroke="#041022" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M19 10l-7-7-7 7" stroke="#041022" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M5 21h14" stroke="#041022" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span>Choose Music File</span>
            </label>

            <div className="hint">Drag & drop or click to upload • MP3, WAV only</div>

            {error && <div className="error">{error}</div>}

            {file && (
              <div className="fileInfo">
                <div className="fileMeta">
                  <strong>{file.name}</strong>
                  <span className="dot">•</span>
                  <span>{bytesToMB(file.size)} MB</span>
                </div>
                <div className="actions">
                  <audio controls ref={audioRef} src={URL.createObjectURL(file)} />
                  <button onClick={removeFile} className="smallBtn">Remove</button>
                </div>
              </div>
            )}

            {genre && (
              <div className="result">
                Predicted genre: <strong>{genre}</strong>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
