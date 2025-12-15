import React, { useState } from 'react';
import './App.css';
import FileUploader from './components/FileUploader';
import ImageViewer from './components/ImageViewer';
import MetricsPanel from './components/MetricsPanel';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🫘 Liver Segmentation Service</h1>
        <p>Автоматическая сегментация печени на КТ-снимках</p>
      </header>

      <main className="container">
        <section className="upload-section">
          <FileUploader onUpload={handleUpload} loading={loading} />
        </section>

        {error && (
          <div className="error-message">
            ❌ Ошибка: {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Обработка изображения...</p>
          </div>
        )}

        {result && (
          <div className="results">
            <section className="viewer-section">
              <h2>Результаты сегментации</h2>
              <ImageViewer 
                originalUrl={`http://localhost:8000${result.original_url}`}
                maskUrl={`http://localhost:8000${result.mask_url}`}
              />
            </section>

            <section className="metrics-section">
              <MetricsPanel metrics={result.metrics} />
            </section>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>© 2025 Liver Segmentation Project | УрФУ Radio Faculty</p>
      </footer>
    </div>
  );
}

export default App;