import React from 'react';

const MetricsPanel = ({ metrics }) => {
  return (
    <div className="metrics-panel">
      <h2>📊 Метрики сегментации</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">📐</div>
          <div className="metric-content">
            <label>Площадь (пиксели)</label>
            <span className="metric-value">{metrics.area_pixels.toLocaleString()}</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🫘</div>
          <div className="metric-content">
            <label>Объем (мм³)</label>
            <span className="metric-value">{metrics.volume_mm3.toLocaleString('ru-RU', { maximumFractionDigits: 0 })}</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">💧</div>
          <div className="metric-content">
            <label>Объем (мл)</label>
            <span className="metric-value">{metrics.volume_ml.toLocaleString('ru-RU', { maximumFractionDigits: 2 })}</span>
          </div>
        </div>
      </div>

      <div className="metric-info">
        <p>✅ Сегментация завершена успешно</p>
        <p className="small-text">Метрики рассчитаны на основе выделенной маски печени</p>
      </div>
    </div>
  );
};

export default MetricsPanel;