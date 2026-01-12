import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiUploadCloud, FiTrendingUp, FiTrendingDown, FiAlertCircle, 
  FiCheckCircle, FiBarChart2, FiPieChart, FiActivity, FiDollarSign,
  FiCalendar, FiUsers, FiRefreshCw, FiArrowRight
} from 'react-icons/fi';
import './Forecasting.css';

const API_BASE_URL = '/api';

const Forecasting = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [forecastData, setForecastData] = useState(null);
  const [currentPortfolio, setCurrentPortfolio] = useState(null);
  const [error, setError] = useState(null);
  const [step, setStep] = useState('upload'); // upload, analysis, complete
  const [pollingAttempts, setPollingAttempts] = useState(0);
  const [processingMessage, setProcessingMessage] = useState('File ingestion in progress...');

  useEffect(() => {
    fetchCurrentPortfolio();
  }, []);

  const fetchCurrentPortfolio = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/portfolio/kpis`);
      if (response.ok) {
        const data = await response.json();
        setCurrentPortfolio(data);
      }
    } catch (err) {
      console.error('Error fetching portfolio:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Upload with forecasting status
      const uploadResponse = await fetch(`${API_BASE_URL}/forecasting/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }

      const uploadResult = await uploadResponse.json();
      
      // Start processing
      setUploading(false);
      setStep('processing');

      // Poll for processing completion
      const leaseId = uploadResult.lease_id;
      pollForCompletion(leaseId);

    } catch (err) {
      setError(err.message || 'Failed to upload file');
      setUploading(false);
    }
  };

  const pollForCompletion = async (leaseId) => {
    const maxAttempts = 180; // 6 minutes max (180 * 2s = 360s)
    let attempts = 0;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setError('Processing timed out after 6 minutes. The pipeline may still be running - please check back later.');
        return;
      }

      try {
        console.log(`Polling attempt ${attempts + 1}/${maxAttempts} for lease ${leaseId}`);
        
        const response = await fetch(`${API_BASE_URL}/forecasting/impact/${leaseId}`);
        
        // Log the raw response
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        const data = await response.json();
        
        console.log('Poll response data:', data);
        
        if (response.status === 202) {
          // Still processing
          const message = data.message || 'Processing...';
          console.log('Status 202 - Still processing:', message);
          setProcessingMessage(message);
          setPollingAttempts(attempts + 1);
        } else if (response.ok && data.status === 'ready') {
          // Processing complete!
          console.log('✓ Extraction complete, showing analysis');
          setForecastData(data);
          setStep('analysis');
          return;
        } else if (data.error) {
          // Error occurred
          console.error('API returned error:', data.error);
          setError(data.error || 'Failed to process lease');
          return;
        } else {
          // Unexpected response
          console.warn('Unexpected response:', { status: response.status, data });
        }
      } catch (err) {
        console.error('Polling error:', err);
        // Don't fail on network errors, just continue polling
      }

      attempts++;
      // Adaptive polling: start with 2s, increase to 5s after 30 attempts
      const pollInterval = attempts > 30 ? 5000 : 2000;
      setTimeout(poll, pollInterval);
    };

    poll();
  };

  const handleAddToPortfolio = async () => {
    if (!forecastData) return;

    try {
      const response = await fetch(`${API_BASE_URL}/forecasting/approve/${forecastData.lease_id}`, {
        method: 'POST',
      });

      if (response.ok) {
        setStep('complete');
        // Refresh portfolio data
        fetchCurrentPortfolio();
      } else {
        throw new Error('Failed to add to portfolio');
      }
    } catch (err) {
      setError(err.message || 'Failed to add lease to portfolio');
    }
  };

  const handleReset = () => {
    setFile(null);
    setForecastData(null);
    setStep('upload');
    setError(null);
    setPollingAttempts(0);
    setProcessingMessage('File ingestion in progress...');
  };

  const renderUploadSection = () => (
    <motion.div 
      className="forecast-upload-section"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="forecast-header">
        <FiActivity size={48} color="#FF3621" />
        <h2>Lease Impact Forecasting</h2>
        <p className="forecast-subtitle">
          Upload a potential lease to analyze its impact on your portfolio before committing
        </p>
      </div>

      <div className="upload-zone">
        <input
          type="file"
          id="forecast-file"
          accept=".pdf,.docx,.doc"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <label htmlFor="forecast-file" className="upload-label">
          <FiUploadCloud size={64} color="#FF3621" />
          <h3>Drop lease document here</h3>
          <p>or click to browse</p>
          {file && (
            <div className="selected-file">
              <FiCheckCircle size={20} color="#00FF00" />
              <span>{file.name}</span>
            </div>
          )}
        </label>
      </div>

      {error && (
        <div className="error-message">
          <FiAlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <button 
        className="forecast-button primary"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? (
          <>
            <FiRefreshCw size={20} className="spinning" />
            Uploading...
          </>
        ) : (
          <>
            <FiBarChart2 size={20} />
            Analyze Impact
          </>
        )}
      </button>

      {currentPortfolio && (
        <div className="current-portfolio-summary">
          <h3>Current Portfolio Snapshot</h3>
          <div className="forecast-kpi-strip">
            <div className="forecast-kpi-item">
              <div className="forecast-kpi-icon">
                <FiUsers size={20} />
              </div>
              <div className="forecast-kpi-content">
                <div className="forecast-kpi-label">Total Leases</div>
                <div className="forecast-kpi-value">{currentPortfolio.total_leases}</div>
              </div>
            </div>
            <div className="forecast-kpi-divider"></div>
            
            <div className="forecast-kpi-item">
              <div className="forecast-kpi-icon">
                <FiAlertCircle size={20} />
              </div>
              <div className="forecast-kpi-content">
                <div className="forecast-kpi-label">Avg Risk Score</div>
                <div className="forecast-kpi-value">{currentPortfolio.avg_risk_score?.toFixed(1)}/100</div>
              </div>
            </div>
            <div className="forecast-kpi-divider"></div>
            
            <div className="forecast-kpi-item">
              <div className="forecast-kpi-icon">
                <FiActivity size={20} />
              </div>
              <div className="forecast-kpi-content">
                <div className="forecast-kpi-label">Portfolio WALT</div>
                <div className="forecast-kpi-value">{currentPortfolio.portfolio_walt?.toFixed(1)} yrs</div>
              </div>
            </div>
            <div className="forecast-kpi-divider"></div>
            
            <div className="forecast-kpi-item">
              <div className="forecast-kpi-icon">
                <FiDollarSign size={20} />
              </div>
              <div className="forecast-kpi-content">
                <div className="forecast-kpi-label">Avg Rent PSF</div>
                <div className="forecast-kpi-value">${currentPortfolio.avg_rent_psf?.toFixed(2)}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );

  const renderProcessingSection = () => (
    <motion.div 
      className="forecast-processing"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="processing-animation">
        <motion.div
          className="processing-circle"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <FiActivity size={64} color="#FF3621" />
        </motion.div>
      </div>
      <h2>Analyzing Lease Impact...</h2>
      <p className="processing-steps">
        {processingMessage}
      </p>
      <div className="processing-info">
        <p className="polling-info">
          Polling attempt {pollingAttempts} • Estimated time: 2-3 minutes
        </p>
        <p className="processing-hint">
          The AI pipeline is extracting data from your document. This typically takes 2-3 minutes.
        </p>
      </div>
    </motion.div>
  );

  const renderAnalysisSection = () => {
    if (!forecastData) return null;

    const { current, projected, impact, new_lease } = forecastData;

    return (
      <motion.div 
        className="forecast-analysis"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="analysis-header">
          <FiPieChart size={48} color="#FF3621" />
          <h2>Portfolio Impact Analysis</h2>
          <p className="analysis-subtitle">
            Here's how adding this lease would affect your portfolio
          </p>
        </div>

        {/* New Lease Summary */}
        <div className="new-lease-card">
          <h3>
            <FiCalendar size={24} color="#FF3621" />
            Proposed Lease Details
          </h3>
          <div className="lease-details-grid">
            <div className="detail-item">
              <span className="detail-label">Tenant</span>
              <span className="detail-value">{new_lease.tenant_name}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Property</span>
              <span className="detail-value">{new_lease.property_id || 'N/A'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Square Feet</span>
              <span className="detail-value">{new_lease.square_footage?.toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Annual Rent</span>
              <span className="detail-value">${new_lease.estimated_annual_rent?.toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Lease Term</span>
              <span className="detail-value">{new_lease.term_months} months</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Risk Score</span>
              <span className={`detail-value risk-${getRiskLevel(new_lease.risk_score)}`}>
                {new_lease.risk_score?.toFixed(1)}/100
              </span>
            </div>
          </div>
        </div>

        {/* Impact Metrics */}
        <div className="impact-section">
          <h3>Portfolio Impact Metrics</h3>
          <div className="metrics-comparison">
            
            {/* Total Leases */}
            <div className="metric-comparison-card">
              <div className="metric-icon">
                <FiUsers size={32} color="#FF3621" />
              </div>
              <div className="metric-content">
                <div className="metric-label">Total Leases</div>
                <div className="metric-values">
                  <span className="current-value">{current.total_leases}</span>
                  <FiArrowRight size={20} color="#6B6B6B" />
                  <span className="projected-value">{projected.total_leases}</span>
                </div>
                <div className={`metric-change ${impact.leases_change >= 0 ? 'positive' : 'negative'}`}>
                  {impact.leases_change > 0 ? <FiTrendingUp size={16} /> : <FiTrendingDown size={16} />}
                  +{impact.leases_change} lease
                </div>
              </div>
            </div>

            {/* Risk Score */}
            <div className="metric-comparison-card">
              <div className="metric-icon">
                <FiAlertCircle size={32} color="#FF3621" />
              </div>
              <div className="metric-content">
                <div className="metric-label">Avg Risk Score</div>
                <div className="metric-values">
                  <span className="current-value">{current.avg_risk_score?.toFixed(1)}</span>
                  <FiArrowRight size={20} color="#6B6B6B" />
                  <span className="projected-value">{projected.avg_risk_score?.toFixed(1)}</span>
                </div>
                <div className={`metric-change ${impact.risk_change <= 0 ? 'positive' : 'negative'}`}>
                  {impact.risk_change > 0 ? <FiTrendingUp size={16} /> : <FiTrendingDown size={16} />}
                  {impact.risk_change > 0 ? '+' : ''}{impact.risk_change?.toFixed(1)} pts
                </div>
              </div>
            </div>

            {/* WALT */}
            <div className="metric-comparison-card">
              <div className="metric-icon">
                <FiCalendar size={32} color="#8B4513" />
              </div>
              <div className="metric-content">
                <div className="metric-label">Portfolio WALT</div>
                <div className="metric-values">
                  <span className="current-value">{current.portfolio_walt?.toFixed(1)} yrs</span>
                  <FiArrowRight size={20} color="#6B6B6B" />
                  <span className="projected-value">{projected.portfolio_walt?.toFixed(1)} yrs</span>
                </div>
                <div className={`metric-change ${impact.walt_change >= 0 ? 'positive' : 'negative'}`}>
                  {impact.walt_change > 0 ? <FiTrendingUp size={16} /> : <FiTrendingDown size={16} />}
                  {impact.walt_change > 0 ? '+' : ''}{impact.walt_change?.toFixed(2)} yrs
                </div>
              </div>
            </div>

            {/* Avg Rent PSF */}
            <div className="metric-comparison-card">
              <div className="metric-icon">
                <FiDollarSign size={32} color="#8B4513" />
              </div>
              <div className="metric-content">
                <div className="metric-label">Avg Rent PSF</div>
                <div className="metric-values">
                  <span className="current-value">${current.avg_rent_psf?.toFixed(2)}</span>
                  <FiArrowRight size={20} color="#6B6B6B" />
                  <span className="projected-value">${projected.avg_rent_psf?.toFixed(2)}</span>
                </div>
                <div className={`metric-change ${impact.rent_psf_change >= 0 ? 'positive' : 'negative'}`}>
                  {impact.rent_psf_change > 0 ? <FiTrendingUp size={16} /> : <FiTrendingDown size={16} />}
                  {impact.rent_psf_change > 0 ? '+' : ''}${impact.rent_psf_change?.toFixed(2)}
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Risk Analysis */}
        <div className="risk-analysis-section">
          <h3>Risk Assessment</h3>
          <div className="risk-cards">
            <div className={`risk-card ${impact.risk_change > 5 ? 'warning' : impact.risk_change < -5 ? 'good' : 'neutral'}`}>
              <FiAlertCircle size={32} />
              <h4>Overall Risk Impact</h4>
              <p>
                {impact.risk_change > 5 
                  ? `Adding this lease will increase portfolio risk by ${impact.risk_change.toFixed(1)} points. Consider the tenant's industry and lease terms.`
                  : impact.risk_change < -5
                  ? `This lease will improve portfolio diversification and reduce average risk by ${Math.abs(impact.risk_change).toFixed(1)} points.`
                  : `This lease has a neutral impact on overall portfolio risk (${impact.risk_change.toFixed(1)} point change).`
                }
              </p>
            </div>

            <div className={`risk-card ${impact.walt_change > 0 ? 'good' : 'warning'}`}>
              <FiCalendar size={32} />
              <h4>Lease Duration</h4>
              <p>
                {impact.walt_change > 0 
                  ? `The ${new_lease.term_months}-month term extends portfolio WALT by ${impact.walt_change.toFixed(2)} years, providing more stability.`
                  : `Shorter lease term reduces WALT by ${Math.abs(impact.walt_change).toFixed(2)} years, increasing rollover risk.`
                }
              </p>
            </div>

            <div className={`risk-card ${impact.rent_psf_change > 0 ? 'good' : 'neutral'}`}>
              <FiDollarSign size={32} />
              <h4>Revenue Impact</h4>
              <p>
                This lease adds ${new_lease.estimated_annual_rent?.toLocaleString()} in annual revenue
                {impact.rent_psf_change > 0 
                  ? ` and improves average rent PSF by $${impact.rent_psf_change.toFixed(2)}.`
                  : ` but slightly lowers average rent PSF by $${Math.abs(impact.rent_psf_change).toFixed(2)}.`
                }
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="forecast-actions">
          <button className="forecast-button secondary" onClick={handleReset}>
            <FiRefreshCw size={20} />
            Analyze Another Lease
          </button>
          <button className="forecast-button primary large" onClick={handleAddToPortfolio}>
            <FiCheckCircle size={24} />
            Add to Portfolio
          </button>
        </div>
      </motion.div>
    );
  };

  const renderCompleteSection = () => (
    <motion.div 
      className="forecast-complete"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="success-icon">
        <FiCheckCircle size={80} color="#00FF00" />
      </div>
      <h2>Lease Added to Portfolio!</h2>
      <p>The lease has been successfully verified and added to your portfolio.</p>
      <div className="complete-actions">
        <button className="forecast-button secondary" onClick={handleReset}>
          <FiUploadCloud size={20} />
          Forecast Another Lease
        </button>
        <button className="forecast-button primary" onClick={() => window.location.href = '#'}>
          <FiBarChart2 size={20} />
          View Updated Portfolio
        </button>
      </div>
    </motion.div>
  );

  const getRiskLevel = (score) => {
    if (score >= 75) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  };

  return (
    <div className="forecasting">
      <div className="forecasting-container">
        <AnimatePresence mode="wait">
          {step === 'upload' && renderUploadSection()}
          {step === 'processing' && renderProcessingSection()}
          {step === 'analysis' && renderAnalysisSection()}
          {step === 'complete' && renderCompleteSection()}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Forecasting;

