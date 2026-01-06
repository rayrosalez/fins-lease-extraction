import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiUploadCloud, FiFile, FiCheck, FiX, FiClock, FiEdit2, FiSave, FiRefreshCw, FiTrash2 } from 'react-icons/fi';
import ProcessingAnimation from './ProcessingAnimation';
import ValidationForm from './ValidationForm';
import EnrichmentValidation from './EnrichmentValidation';
import './Upload.css';

const Upload = () => {
  const [uploadState, setUploadState] = useState('idle');
  const [selectedFile, setSelectedFile] = useState(null);
  const [processingStage, setProcessingStage] = useState(0);
  const [extractedData, setExtractedData] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [isTimeout, setIsTimeout] = useState(false);
  
  // Validation section state
  const [newRecords, setNewRecords] = useState([]);
  const [originalRecords, setOriginalRecords] = useState({}); // Track original values
  const [selectedRecords, setSelectedRecords] = useState([]);
  const [editingRecord, setEditingRecord] = useState(null);
  const [editValues, setEditValues] = useState({});
  const [validationLoading, setValidationLoading] = useState(false);
  const [validationMessage, setValidationMessage] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [validatedLeaseData, setValidatedLeaseData] = useState(null); // Store validated lease for enrichment

  // Fetch new records on component mount
  useEffect(() => {
    fetchNewRecords();
  }, []);

  const fetchNewRecords = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('http://localhost:5001/api/records/new');
      const data = await response.json();
      
      if (response.ok) {
        setNewRecords(data);
        // Store original records for tracking edits
        const originals = {};
        data.forEach(record => {
          originals[record.extraction_id] = { ...record };
        });
        setOriginalRecords(originals);
      } else {
        console.error('Failed to fetch new records:', data.error);
      }
    } catch (err) {
      console.error('Error fetching new records:', err);
    } finally {
      setRefreshing(false);
    }
  };

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
      // Upload: ~2 sec, Parsing: ~1-2 min, Extraction: ~2-4 min = ~7.5 mins total timeout
      const checkProcessing = async () => {
        const maxAttempts = 90; // Check for up to ~7.5 minutes (90 * 5 sec)
        const pollInterval = 5000; // Check every 5 seconds
        
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
          // Update stage display based on time elapsed
          // Stage 1: Uploading (0-6 attempts = 0-30 sec)
          // Stage 2: Parsing (6-30 attempts = 30 sec - 2.5 min)
          // Stage 3: Extracting (30-78 attempts = 2.5 min - 6.5 min)
          // Stage 4: Validating (78-90 attempts = 6.5-7.5 min)
          if (attempt < 6) setProcessingStage(1);
          else if (attempt < 30) setProcessingStage(2);
          else if (attempt < 78) setProcessingStage(3);
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
              console.log(`Check attempt ${attempt + 1}/${maxAttempts}: Still processing... (${Math.floor(attempt * 5 / 60)} min elapsed)`);
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
        
        // Timeout after all attempts (7.5 minutes)
        console.log('Processing timeout reached after 7.5 minutes');
        setIsTimeout(true);
        setError('AI extraction is taking longer than expected (>7 minutes). Your file was uploaded successfully and extraction may still be running. Please check the "Validate Extracted Records" section below to review and validate the data when ready.');
        setUploadState('timeout_with_validation');
        
        // Refresh the NEW records list so user can validate when ready
        fetchNewRecords();
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
      
      // Store the validated lease data for enrichment step
      setValidatedLeaseData({
        ...extractedData,
        ...validatedData
      });
      
      // Move to enrichment step instead of success
      setUploadState('enrichment');
      
    } catch (err) {
      console.error('Validation error:', err);
      setError(`Failed to save validation: ${err.message}`);
      setUploadState('error');
    }
  };

  const handleEnrichmentComplete = () => {
    console.log('Enrichment complete');
    setUploadState('success');
    setUploadSuccess(true);
    
    setTimeout(() => {
      resetUpload();
    }, 3000);
  };

  const handleSkipEnrichment = () => {
    console.log('Enrichment skipped');
    setUploadState('success');
    setUploadSuccess(true);
    
    setTimeout(() => {
      resetUpload();
    }, 3000);
  };

  const resetUpload = () => {
    setUploadState('idle');
    setSelectedFile(null);
    setProcessingStage(0);
    setExtractedData(null);
    setValidatedLeaseData(null);
    setUploadSuccess(false);
    setError(null);
    setIsTimeout(false);
    fetchNewRecords(); // Refresh the validation list
  };

  // Validation section handlers
  const handleRecordSelect = (extractionId) => {
    setSelectedRecords(prev => {
      if (prev.includes(extractionId)) {
        return prev.filter(id => id !== extractionId);
      } else {
        return [...prev, extractionId];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedRecords.length === newRecords.length) {
      setSelectedRecords([]);
    } else {
      setSelectedRecords(newRecords.map(r => r.extraction_id));
    }
  };

  const handleEditRecord = (record) => {
    setEditingRecord(record.extraction_id);
    setEditValues(record);
  };

  const handleSaveEdit = () => {
    // Update the record in the local state
    setNewRecords(prev => 
      prev.map(r => r.extraction_id === editingRecord ? editValues : r)
    );
    setEditingRecord(null);
  };

  const handleCancelEdit = () => {
    setEditingRecord(null);
    setEditValues({});
  };

  const handleFieldChange = (field, value) => {
    setEditValues(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleValidateSelected = async () => {
    if (selectedRecords.length === 0) {
      setValidationMessage({ type: 'error', text: 'Please select at least one record to validate' });
      return;
    }

    setValidationLoading(true);
    setValidationMessage(null);

    try {
      // Prepare records with their updates
      const recordsToValidate = selectedRecords.map(id => {
        const record = newRecords.find(r => r.extraction_id === id);
        const originalRecord = originalRecords[id] || {};
        
        // Find fields that were edited
        const updates = {};
        Object.keys(record).forEach(key => {
          if (record[key] !== originalRecord[key] && key !== 'extraction_id') {
            updates[key] = record[key];
          }
        });

        return {
          extraction_id: id,
          updates: updates
        };
      });

      const response = await fetch('http://localhost:5001/api/records/validate-multiple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ records: recordsToValidate })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to validate records');
      }

      setValidationMessage({ 
        type: 'success', 
        text: `Successfully validated ${selectedRecords.length} record(s)!` 
      });
      
      // Clear selections and refresh
      setSelectedRecords([]);
      
      // Refresh after a short delay to show success message
      setTimeout(() => {
        fetchNewRecords();
        setValidationMessage(null);
      }, 2000);

    } catch (err) {
      console.error('Validation error:', err);
      setValidationMessage({ 
        type: 'error', 
        text: `Failed to validate: ${err.message}` 
      });
    } finally {
      setValidationLoading(false);
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedRecords.length === 0) {
      setValidationMessage({ type: 'error', text: 'Please select at least one record to delete' });
      return;
    }

    // Confirm deletion
    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${selectedRecords.length} record(s)? This action cannot be undone.`
    );

    if (!confirmDelete) return;

    setValidationLoading(true);
    setValidationMessage(null);

    try {
      const response = await fetch('http://localhost:5001/api/records/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ extraction_ids: selectedRecords })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to delete records');
      }

      setValidationMessage({ 
        type: 'success', 
        text: `Successfully deleted ${selectedRecords.length} record(s)!` 
      });
      
      // Clear selections and refresh
      setSelectedRecords([]);
      
      // Refresh after a short delay to show success message
      setTimeout(() => {
        fetchNewRecords();
        setValidationMessage(null);
      }, 2000);

    } catch (err) {
      console.error('Delete error:', err);
      setValidationMessage({ 
        type: 'error', 
        text: `Failed to delete: ${err.message}` 
      });
    } finally {
      setValidationLoading(false);
    }
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
          <h1 className="upload-title">Upload and Validate</h1>
          <p className="upload-subtitle">
            Upload new lease documents and validate extracted data
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

          {uploadState === 'enrichment' && validatedLeaseData && (
            <EnrichmentValidation
              leaseRecord={validatedLeaseData}
              onComplete={handleEnrichmentComplete}
              onCancel={handleSkipEnrichment}
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

          {uploadState === 'timeout_with_validation' && (
            <motion.div
              className="timeout-validation-state"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="timeout-icon">
                <FiClock size={48} />
              </div>
              <h2>AI Extraction Taking Longer Than Expected</h2>
              <p>{error}</p>
              <div className="timeout-actions">
                <button onClick={() => {
                  setUploadState('idle');
                  fetchNewRecords();
                }} className="check-validation-button">
                  ↓ Check Validation Section Below
                </button>
                <button onClick={resetUpload} className="retry-button-secondary">
                  Upload Another File
                </button>
              </div>
              <div className="timeout-info">
                <p><strong>What happened?</strong></p>
                <p>Your PDF was uploaded successfully, but the AI extraction is taking longer than usual (typical: 2-4 minutes, yours: >7 minutes). This can happen with:</p>
                <ul>
                  <li>Large PDF files (>50 pages)</li>
                  <li>Complex lease agreements</li>
                  <li>Heavy system load</li>
                </ul>
                <p><strong>Next steps:</strong></p>
                <p>1. Scroll down to "Validate Extracted Records" section</p>
                <p>2. Wait 1-2 minutes, then click the section to refresh</p>
                <p>3. Your lease should appear with status "NEW"</p>
                <p>4. Review and validate the extracted data</p>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Validation Section */}
        <motion.div
          className="validation-section"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="validation-header">
            <h2 className="validation-title">Validate Extracted Records</h2>
            <p className="validation-subtitle">
              Review and validate records with "New" status before they are promoted to the portfolio
            </p>
            <button 
              className="refresh-records-button"
              onClick={fetchNewRecords}
              disabled={refreshing}
            >
              <FiRefreshCw className={refreshing ? 'spinning' : ''} size={18} />
              {refreshing ? 'Refreshing...' : 'Refresh Records'}
            </button>
          </div>

          {validationMessage && (
            <motion.div
              className={`validation-message ${validationMessage.type}`}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
            >
              {validationMessage.type === 'success' ? <FiCheck size={20} /> : <FiX size={20} />}
              {validationMessage.text}
            </motion.div>
          )}

          {newRecords.length === 0 ? (
            <div className="no-records">
              <FiCheck size={48} />
              <p>All records have been validated! Upload a new document to see pending records here.</p>
            </div>
          ) : (
            <>
              <div className="validation-actions">
                <button 
                  className="select-all-btn"
                  onClick={handleSelectAll}
                >
                  {selectedRecords.length === newRecords.length ? 'Deselect All' : 'Select All'}
                </button>
                <button 
                  className="delete-btn"
                  onClick={handleDeleteSelected}
                  disabled={selectedRecords.length === 0 || validationLoading}
                >
                  <FiTrash2 size={16} />
                  {validationLoading ? 'Deleting...' : `Delete Selected (${selectedRecords.length})`}
                </button>
                <button 
                  className="validate-btn"
                  onClick={handleValidateSelected}
                  disabled={selectedRecords.length === 0 || validationLoading}
                >
                  {validationLoading ? 'Validating...' : `Validate Selected (${selectedRecords.length})`}
                </button>
              </div>

              <div className="records-table">
                <table>
                  <thead>
                    <tr>
                      <th>
                        <input
                          type="checkbox"
                          checked={selectedRecords.length === newRecords.length && newRecords.length > 0}
                          onChange={handleSelectAll}
                        />
                      </th>
                      <th>Tenant</th>
                      <th>Landlord</th>
                      <th>Property City</th>
                      <th>Commencement</th>
                      <th>Expiration</th>
                      <th>Square Feet</th>
                      <th>Rent PSF</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {newRecords.map(record => (
                      <tr key={record.extraction_id} className={editingRecord === record.extraction_id ? 'editing' : ''}>
                        <td>
                          <input
                            type="checkbox"
                            checked={selectedRecords.includes(record.extraction_id)}
                            onChange={() => handleRecordSelect(record.extraction_id)}
                            disabled={editingRecord === record.extraction_id}
                          />
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <input
                              type="text"
                              value={editValues.tenant_name || ''}
                              onChange={(e) => handleFieldChange('tenant_name', e.target.value)}
                            />
                          ) : (
                            record.tenant_name || '-'
                          )}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <input
                              type="text"
                              value={editValues.landlord_name || ''}
                              onChange={(e) => handleFieldChange('landlord_name', e.target.value)}
                            />
                          ) : (
                            record.landlord_name || '-'
                          )}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <input
                              type="text"
                              value={editValues.property_city || ''}
                              onChange={(e) => handleFieldChange('property_city', e.target.value)}
                            />
                          ) : (
                            record.property_city || '-'
                          )}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <input
                              type="date"
                              value={editValues.commencement_date || ''}
                              onChange={(e) => handleFieldChange('commencement_date', e.target.value)}
                            />
                          ) : (
                            record.commencement_date || '-'
                          )}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <input
                              type="date"
                              value={editValues.expiration_date || ''}
                              onChange={(e) => handleFieldChange('expiration_date', e.target.value)}
                            />
                          ) : (
                            record.expiration_date || '-'
                          )}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <input
                              type="number"
                              value={editValues.rentable_square_feet || ''}
                              onChange={(e) => handleFieldChange('rentable_square_feet', e.target.value)}
                            />
                          ) : (
                            record.rentable_square_feet ? Number(record.rentable_square_feet).toLocaleString() : '-'
                          )}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <input
                              type="number"
                              step="0.01"
                              value={editValues.base_rent_psf || ''}
                              onChange={(e) => handleFieldChange('base_rent_psf', e.target.value)}
                            />
                          ) : (
                            record.base_rent_psf ? `$${Number(record.base_rent_psf).toFixed(2)}` : '-'
                          )}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <div className="edit-actions">
                              <button onClick={handleSaveEdit} className="save-btn" title="Save">
                                <FiSave size={16} />
                              </button>
                              <button onClick={handleCancelEdit} className="cancel-btn" title="Cancel">
                                <FiX size={16} />
                              </button>
                            </div>
                          ) : (
                            <button 
                              onClick={() => handleEditRecord(record)} 
                              className="edit-btn"
                              title="Edit"
                            >
                              <FiEdit2 size={16} />
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Upload;

