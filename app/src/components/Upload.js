import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiUploadCloud, FiFile, FiCheck, FiX, FiClock, FiInbox } from 'react-icons/fi';
import ProcessingAnimation from './ProcessingAnimation';
import PendingReviews from './PendingReviews';
import './Upload.css';

const Upload = () => {
  const [tab, setTab] = useState('upload'); // upload | reviews
  const [uploadState, setUploadState] = useState('idle');
  const [selectedFile, setSelectedFile] = useState(null);
  const [processingStage, setProcessingStage] = useState(0);
  const [error, setError] = useState(null);
  const [isTimeout, setIsTimeout] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  // Fetch pending count on mount and periodically
  useEffect(() => {
    const fetchCount = async () => {
      try {
        const res = await fetch('/api/records/count');
        const data = await res.json();
        if (res.ok) setPendingCount(data.count || 0);
      } catch (e) { /* silent */ }
    };
    fetchCount();
    const interval = setInterval(fetchCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please drop a valid PDF file');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadState('uploading');
    setProcessingStage(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Upload failed');
      }

      if (!result.success || !result.file_path) {
        throw new Error('Upload succeeded but no file path returned');
      }

      console.log('File uploaded successfully:', result.file_path);

      setUploadState('processing');
      setProcessingStage(1);

      const checkProcessing = async () => {
        const maxAttempts = 90;
        const pollInterval = 5000;

        for (let attempt = 0; attempt < maxAttempts; attempt++) {
          if (attempt < 6) setProcessingStage(1);
          else if (attempt < 30) setProcessingStage(2);
          else if (attempt < 78) setProcessingStage(3);
          else setProcessingStage(4);

          try {
            const checkResponse = await fetch('/api/check-processing', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ file_path: result.file_path })
            });

            const processResult = await checkResponse.json();

            if (processResult.processed && processResult.record) {
              console.log('Processing complete, record found:', processResult.record);
              setUploadState('upload_success');
              // Refresh pending count
              try {
                const res = await fetch('/api/records/count');
                const data = await res.json();
                if (res.ok) setPendingCount(data.count || 0);
              } catch (e) { /* silent */ }
              return;
            }

            if (!processResult.processed && !processResult.error) {
              console.log(`Check attempt ${attempt + 1}/${maxAttempts}: Still processing...`);
            } else if (processResult.error) {
              console.log(`Check attempt ${attempt + 1}: API error (continuing): ${processResult.error}`);
            }

            await new Promise(resolve => setTimeout(resolve, pollInterval));
          } catch (err) {
            console.log(`Check attempt ${attempt + 1} network error (continuing):`, err.message);
            await new Promise(resolve => setTimeout(resolve, pollInterval));
          }
        }

        console.log('Processing timeout reached after 7.5 minutes');
        setIsTimeout(true);
        setError('AI extraction is taking longer than expected. Your file was uploaded successfully and extraction is still running.');
        setUploadState('timeout_with_validation');
      };

      checkProcessing();

    } catch (err) {
      console.error('Upload error:', err);
      setIsTimeout(false);
      setError(err.message || 'An error occurred during upload. Please try again.');
      setUploadState('error');
    }
  };

  const resetUpload = () => {
    setUploadState('idle');
    setSelectedFile(null);
    setProcessingStage(0);
    setError(null);
    setIsTimeout(false);
  };

  const goToReviews = () => {
    resetUpload();
    setTab('reviews');
  };

  return (
    <div className="upload-page">
      <div className="upload-container">
        <motion.div
          className="upload-header"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="upload-title">Upload & Validate</h1>
          <p className="upload-subtitle">
            Upload new lease documents and review AI-extracted data
          </p>

          <div className="upload-tab-bar">
            <button
              className={`upload-tab ${tab === 'upload' ? 'active' : ''}`}
              onClick={() => setTab('upload')}
            >
              <FiUploadCloud size={18} />
              Upload
            </button>
            <button
              className={`upload-tab ${tab === 'reviews' ? 'active' : ''}`}
              onClick={() => setTab('reviews')}
            >
              <FiInbox size={18} />
              Pending Reviews
              {pendingCount > 0 && <span className="tab-badge">{pendingCount}</span>}
            </button>
          </div>
        </motion.div>

        {tab === 'upload' && (
          <motion.div
            className="upload-content"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            {uploadState === 'idle' && (
              <div
                className="upload-area"
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
              >
                <input
                  type="file"
                  id="file-upload"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
                <label htmlFor="file-upload" className="upload-label">
                  <FiUploadCloud size={64} className="upload-icon" />
                  <h3>Drag & Drop or Click to Upload</h3>
                  <p>Upload PDF lease documents for processing</p>
                </label>

                {selectedFile && (
                  <div className="selected-file">
                    <FiFile size={24} />
                    <span>{selectedFile.name}</span>
                    <button onClick={() => setSelectedFile(null)} className="remove-file">
                      <FiX size={20} />
                    </button>
                  </div>
                )}

                {error && (
                  <div className="error-message">
                    <FiX size={20} />
                    {error}
                  </div>
                )}

                {selectedFile && !error && (
                  <button onClick={handleUpload} className="upload-button">
                    <FiUploadCloud size={20} />
                    Start Processing
                  </button>
                )}
              </div>
            )}

            {uploadState === 'processing' && (
              <ProcessingAnimation stage={processingStage} fileName={selectedFile?.name} />
            )}

            {uploadState === 'upload_success' && (
              <motion.div
                className="success-message"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="success-icon">
                  <FiCheck size={48} />
                </div>
                <h2>Lease Uploaded Successfully!</h2>
                <p>Your document has been processed and is ready for review.</p>
                <button onClick={goToReviews} className="go-to-reviews-button">
                  <FiInbox size={20} />
                  Review Now{pendingCount > 0 ? ` (${pendingCount})` : ''}
                </button>
                <button onClick={resetUpload} className="upload-another-button">
                  Upload Another
                </button>
              </motion.div>
            )}

            {uploadState === 'error' && (
              <motion.div
                className="error-state"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="error-icon">
                  <FiX size={48} />
                </div>
                <h2>Upload Failed</h2>
                <p>{error || 'An unexpected error occurred. Please try again.'}</p>
                <button onClick={resetUpload} className="retry-button">
                  Try Again
                </button>
              </motion.div>
            )}

            {uploadState === 'timeout_with_validation' && (
              <motion.div
                className="success-message"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="success-icon timeout-icon">
                  <FiClock size={48} />
                </div>
                <h2>Processing in Background</h2>
                <p>Your file was uploaded successfully. AI extraction is still running. Your record will appear in Pending Reviews when ready.</p>
                <button onClick={goToReviews} className="go-to-reviews-button">
                  <FiInbox size={20} />
                  Go to Pending Reviews
                </button>
                <button onClick={resetUpload} className="upload-another-button">
                  Upload Another
                </button>
              </motion.div>
            )}
          </motion.div>
        )}

        {tab === 'reviews' && (
          <PendingReviews onCountChange={setPendingCount} />
        )}
      </div>
    </div>
  );
};

export default Upload;
