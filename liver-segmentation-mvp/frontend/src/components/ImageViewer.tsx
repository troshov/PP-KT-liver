import React, { useState } from 'react';

const ImageViewer = ({ originalUrl, maskUrl }) => {
  const [showMask, setShowMask] = useState(true);
  const [opacity, setOpacity] = useState(0.5);

  return (
    <div className="image-viewer">
      <div className="image-container">
        <img src={originalUrl} alt="Original DICOM" className="base-image" />
        {showMask && (
          <img 
            src={maskUrl} 
            alt="Segmentation Mask" 
            className="mask-image"
            style={{ opacity }}
          />
        )}
      </div>

      <div className="controls">
        <button 
          className={`toggle-btn ${showMask ? 'active' : ''}`}
          onClick={() => setShowMask(!showMask)}
        >
          {showMask ? '👁 Скрыть маску' : '👁 Показать маску'}
        </button>

        <div className="opacity-control">
          <label>Прозрачность маски:</label>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.1"
            value={opacity}
            onChange={(e) => setOpacity(e.target.value)}
          />
          <span>{Math.round(opacity * 100)}%</span>
        </div>
      </div>
    </div>
  );
};

export default ImageViewer;