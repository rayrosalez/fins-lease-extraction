import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiUploadCloud, FiFile, FiCheck, FiX, FiClock } from 'react-icons/fi';
import ProcessingAnimation from './ProcessingAnimation';
import ValidationForm from './ValidationForm';
import './Upload.css';

const Upload = () => {
  const [uploadState, setUploadState] = useState('idle');
  const [selectedFile, setSelectedFile] = useState(null);
  const [processingStage, setProcessingStage] = useState(0);
  const [extractedData, setExtractedData] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [isTimeout, setIsTimeout] = useState(false);

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
      // Upload file to Databricks volume
      const response = await fetch('http://localhost:5001/api/upload', {
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
      
      // Upload complete, now start processing stages
      setUploadState('processing');
      setProcessingStage(1);
      
      // Poll for processing completion
      // Upload: ~2 sec, Parsing: ~1 min, Extraction: ~1 min, Validation: ~1 min = ~3 mins total
      const checkProcessing = async () => {
        const maxAttempts = 45; // Check for up to ~4 minutes (buffer time)
        const pollInterval = 5000; // Check every 5 seconds
        
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
          // Update stage display based on time elapsed
          // Stage 1: Uploading (0-6 attempts = 0-30 sec)
          // Stage 2: Parsing (6-18 attempts = 30-90 sec) 
          // Stage 3: Extracting (18-30 attempts = 90-150 sec)
          // Stage 4: Validating (30+ attempts = 150+ sec)
          if (attempt < 6) setProcessingStage(1);
          else if (attempt < 18) setProcessingStage(2);
          else if (attempt < 30) setProcessingStage(3);
          else setProcessingStage(4);
          
          try {
            const checkResponse = await fetch(
              `http://localhost:5001/api/check-processing/${encodeURIComponent(result.file_path)}`
            );
            
            const processResult = await checkResponse.json();
            
            // Check if processing is complete
            if (processResult.processed && processResult.record) {
              console.log('Processing complete, record found:', processResult.record);
              setExtractedData(processResult.record);
              setUploadState('validation');
              return;
            }
            
            // If response indicates still processing (not an error)
            if (!processResult.processed && !processResult.error) {
              console.log(`Check attempt ${attempt + 1}: Still processing...`);
            } else if (processResult.error) {
              // Only log errors, don't fail - might be transient
              console.log(`Check attempt ${attempt + 1}: API error (continuing): ${processResult.error}`);
            }
            
            // Wait before next check
            await new Promise(resolve => setTimeout(resolve, pollInterval));
          } catch (err) {
            console.log(`Check attempt ${attempt + 1} network error (continuing):`, err.message);
            // Continue polling even if individual checks fail
            await new Promise(resolve => setTimeout(resolve, pollInterval));
          }
        }
        
        // Timeout after all attempts
        console.log('Processing timeout reached');
        setIsTimeout(true);
        setError('Processing is taking longer than expected. Your file was uploaded successfully. Please check the Portfolio page in a few minutes to see if the extraction completed.');
        setUploadState('error');
      };

      checkProcessing();

    } catch (err) {
      console.error('Upload error:', err);
      setIsTimeout(false);
      setError(err.message || 'An error occurred during upload. Please try again.');
      setUploadState('error');
    }
  };

  const handleValidationComplete = async (validatedData) => {
    try {
      console.log('Submitting validated data:', validatedData);
      
      // Send validated data to API
      const response = await fetch('http://localhost:5001/api/validate-record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          extraction_id: extractedData.extraction_id,
          updates: validatedData
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Validation failed');
      }

      console.log('Validation successful:', result);
      
      setUploadState('success');
      setUploadSuccess(true);
      
      setTimeout(() => {
        resetUpload();
      }, 3000);
    } catch (err) {
      console.error('Validation error:', err);
      setError(`Failed to save validation: ${err.message}`);
      setUploadState('error');
    }
  };

  const resetUpload = () => {
    setUploadState('idle');
    setSelectedFile(null);
    setProcessingStage(0);
    setExtractedData(null);
    setUploadSuccess(false);
    setError(null);
    setIsTimeout(false);
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
          <h1 className="upload-title">Upload Lease Documents</h1>
          <p className="upload-subtitle">
            Upload PDF lease documents for AI-powered extraction and validation
          </p>
        </motion.div>

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

          {uploadState === 'validation' && extractedData && (
            <ValidationForm
              record={extractedData}
              onSubmit={handleValidationComplete}
              onCancel={resetUpload}
            />
          )}

          {uploadState === 'success' && (
            <motion.div
              className="success-message"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="success-icon">
                <FiCheck size={48} />
              </div>
              <h2>Lease Successfully Validated!</h2>
              <p>Your lease has been added to the portfolio and is now available in all views.</p>
            </motion.div>
          )}

          {uploadState === 'error' && (
            <motion.div
              className={`error-state ${isTimeout ? 'timeout-state' : ''}`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className={`error-icon ${isTimeout ? 'timeout-icon' : ''}`}>
                {isTimeout ? <FiClock size={48} /> : <FiX size={48} />}
              </div>
              <h2>{isTimeout ? 'Processing Timeout' : 'Upload Failed'}</h2>
              <p>{error || 'An unexpected error occurred. Please try again.'}</p>
              <button onClick={resetUpload} className="retry-button">
                {isTimeout ? 'Upload Another File' : 'Try Again'}
              </button>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Upload;

