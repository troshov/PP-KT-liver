import React, { useState } from 'react';

const FileUploader = ({ onUpload, loading }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      onUpload(file);
    }
  };

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div
      className={`file-uploader ${dragActive ? 'active' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="17 8 12 3 7 8"></polyline>
        <line x1="12" y1="3" x2="12" y2="15"></line>
      </svg>
      
      <h3>Загрузите DICOM файл</h3>
      <p>Перетащите файл сюда или нажмите для выбора</p>
      
      <input
        type="file"
        onChange={handleChange}
        disabled={loading}
        accept=".dcm,.nii,.nifti"
        style={{ display: 'none' }}
        id="file-input"
      />
      
      <label htmlFor="file-input" className="upload-button">
        {loading ? 'Обработка...' : 'Выбрать файл'}
      </label>
    </div>
  );
};

export default FileUploader;