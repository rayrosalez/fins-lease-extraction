import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiRefreshCw, FiX, FiCheck, FiAlertTriangle, FiDatabase, FiUsers, FiHome } from 'react-icons/fi';
import './ResetModal.css';

const ResetModal = ({ isOpen, onClose }) => {
  const [numLeases, setNumLeases] = useState(50);
  const [isResetting, setIsResetting] = useState(false);
  const [progress, setProgress] = useState({ stage: '', percent: 0 });
  const [result, setResult] = useState(null);

  const handleReset = async () => {
    if (!window.confirm(`⚠️ This will DELETE all data and create ${numLeases} new leases.\n\nAre you sure?`)) {
      return;
    }

    setIsResetting(true);
    setResult(null);
    
    try {
      // Stage 1: Purging
      setProgress({ stage: 'Purging existing data...', percent: 10 });
      
      // Small delay to show initial progress
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Stage 2: Optimizing
      setProgress({ stage: 'Optimizing Delta tables...', percent: 25 });
      
      // Make the actual API call
      const response = await fetch('/api/reset-demo-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_leases: numLeases })
      });

      // Stage 3: Generating (happens during API call)
      setProgress({ stage: 'Generating synthetic data...', percent: 60 });
      
      // Small delay to show progress
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Stage 4: Verifying
      setProgress({ stage: 'Verifying data...', percent: 90 });

      const data = await response.json();

      if (response.ok) {
        setProgress({ stage: 'Complete!', percent: 100 });
        setResult({
          success: true,
          message: data.message,
          counts: data.counts,
          leases: data.leases_generated,
          tenants: data.tenants_created,
          landlords: data.landlords_created
        });
        
        // Refresh the page after a short delay to show the new data
        setTimeout(() => {
          window.location.reload();
        }, 3000);
      } else {
        setProgress({ stage: 'Error', percent: 0 });
        setResult({
          success: false,
          error: data.error || 'Unknown error occurred'
        });
      }
    } catch (error) {
      setProgress({ stage: 'Error', percent: 0 });
      setResult({
        success: false,
        error: error.message
      });
    } finally {
      setIsResetting(false);
    }
  };

  const handleClose = () => {
    if (!isResetting) {
      setProgress({ stage: '', percent: 0 });
      setResult(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div 
        className="reset-modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={handleClose}
      >
        <motion.div 
          className="reset-modal-content"
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="reset-modal-header">
            <div className="reset-modal-title">
              <FiRefreshCw size={24} color="#FF3621" />
              <h2>Reset Demo Data</h2>
            </div>
            {!isResetting && (
              <button className="reset-modal-close" onClick={handleClose}>
                <FiX size={24} />
              </button>
            )}
          </div>

          <div className="reset-modal-body">
            {!isResetting && !result && (
              <>
                <div className="reset-warning">
                  <FiAlertTriangle size={20} color="#F59E0B" />
                  <p>This will permanently delete all existing data and generate fresh synthetic leases.</p>
                </div>

                <div className="reset-input-group">
                  <label htmlFor="numLeases">Number of Leases to Generate</label>
                  <input
                    id="numLeases"
                    type="number"
                    min="10"
                    max="500"
                    value={numLeases}
                    onChange={(e) => setNumLeases(Math.min(500, Math.max(10, parseInt(e.target.value) || 50)))}
                    className="reset-input"
                  />
                  <span className="reset-input-hint">Recommended: 50-100 leases</span>
                </div>

                <div className="reset-preview">
                  <h4>What will be generated:</h4>
                  <ul>
                    <li>
                      <FiDatabase size={16} />
                      <span>{numLeases} verified leases (directly in silver layer)</span>
                    </li>
                    <li>
                      <FiUsers size={16} />
                      <span>~{Math.ceil(numLeases * 0.7)} unique tenants with enrichment</span>
                    </li>
                    <li>
                      <FiHome size={16} />
                      <span>~20 landlords (major REITs) with enrichment</span>
                    </li>
                  </ul>
                </div>

                <div className="reset-modal-actions">
                  <button className="reset-btn-cancel" onClick={handleClose}>
                    Cancel
                  </button>
                  <button className="reset-btn-confirm" onClick={handleReset}>
                    <FiRefreshCw size={18} />
                    Reset & Generate
                  </button>
                </div>
              </>
            )}

            {isResetting && (
              <div className="reset-progress-container">
                <div className="reset-progress-stage">
                  <div className="reset-spinner">
                    <FiRefreshCw size={32} />
                  </div>
                  <h3>{progress.stage}</h3>
                </div>

                <div className="reset-progress-bar">
                  <div 
                    className="reset-progress-fill"
                    style={{ width: `${progress.percent}%` }}
                  />
                </div>

                <p className="reset-progress-text">
                  This may take 30-90 seconds depending on the number of leases...
                </p>

                <div className="reset-steps">
                  <div className={`reset-step ${progress.percent >= 10 ? 'active' : ''}`}>
                    <div className="reset-step-icon">
                      {progress.percent >= 30 ? <FiCheck /> : '1'}
                    </div>
                    <span>Purge Data</span>
                  </div>
                  <div className={`reset-step ${progress.percent >= 30 ? 'active' : ''}`}>
                    <div className="reset-step-icon">
                      {progress.percent >= 50 ? <FiCheck /> : '2'}
                    </div>
                    <span>Optimize Tables</span>
                  </div>
                  <div className={`reset-step ${progress.percent >= 50 ? 'active' : ''}`}>
                    <div className="reset-step-icon">
                      {progress.percent >= 90 ? <FiCheck /> : '3'}
                    </div>
                    <span>Generate Data</span>
                  </div>
                  <div className={`reset-step ${progress.percent >= 90 ? 'active' : ''}`}>
                    <div className="reset-step-icon">
                      {progress.percent >= 100 ? <FiCheck /> : '4'}
                    </div>
                    <span>Verify</span>
                  </div>
                </div>
              </div>
            )}

            {result && (
              <div className={`reset-result ${result.success ? 'success' : 'error'}`}>
                {result.success ? (
                  <>
                    <div className="reset-result-icon success">
                      <FiCheck size={48} />
                    </div>
                    <h3>Reset Complete! ✨</h3>
                    <p>{result.message}</p>
                    
                    <div className="reset-result-stats">
                      <div className="reset-stat">
                        <FiDatabase size={24} />
                        <div>
                          <strong>{result.leases}</strong>
                          <span>Leases</span>
                        </div>
                      </div>
                      <div className="reset-stat">
                        <FiUsers size={24} />
                        <div>
                          <strong>{result.tenants}</strong>
                          <span>Tenants</span>
                        </div>
                      </div>
                      <div className="reset-stat">
                        <FiHome size={24} />
                        <div>
                          <strong>{result.landlords}</strong>
                          <span>Landlords</span>
                        </div>
                      </div>
                    </div>

                    <div className="reset-next-steps">
                      <h4>Next Steps:</h4>
                      <ul>
                        <li>Navigate to Portfolio page to see the new data</li>
                        <li>Check Risk Assessment for enriched profiles</li>
                        <li>All leases are marked as VERIFIED</li>
                      </ul>
                    </div>

                    <button className="reset-btn-done" onClick={handleClose}>
                      <FiCheck size={18} />
                      Done
                    </button>
                  </>
                ) : (
                  <>
                    <div className="reset-result-icon error">
                      <FiAlertTriangle size={48} />
                    </div>
                    <h3>Reset Failed</h3>
                    <p className="reset-error-message">{result.error}</p>
                    
                    <div className="reset-error-help">
                      <h4>Troubleshooting:</h4>
                      <ul>
                        <li>Check that Databricks SQL Warehouse is running</li>
                        <li>Verify backend server is running</li>
                        <li>Check browser console for detailed errors</li>
                        <li>Review backend logs for more information</li>
                      </ul>
                    </div>

                    <button className="reset-btn-done error" onClick={handleClose}>
                      Close
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ResetModal;
