import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCheck, FiX, FiEdit2, FiSave, FiRefreshCw, FiTrash2, FiArrowLeft, FiInbox } from 'react-icons/fi';
import ValidationForm from './ValidationForm';
import EnrichmentValidation from './EnrichmentValidation';
import './PendingReviews.css';

const PendingReviews = ({ onCountChange }) => {
  const [view, setView] = useState('list'); // list | validation | enrichment
  const [records, setRecords] = useState([]);
  const [originalRecords, setOriginalRecords] = useState({});
  const [selectedRecords, setSelectedRecords] = useState([]);
  const [editingRecord, setEditingRecord] = useState(null);
  const [editValues, setEditValues] = useState({});
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [message, setMessage] = useState(null);

  // For validation/enrichment flow
  const [activeRecord, setActiveRecord] = useState(null);
  const [validatedLeaseData, setValidatedLeaseData] = useState(null);

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('/api/records/new');
      const data = await response.json();
      if (response.ok) {
        const sorted = data.sort((a, b) => new Date(b.uploaded_at || 0) - new Date(a.uploaded_at || 0));
        setRecords(sorted);
        const originals = {};
        sorted.forEach(r => { originals[r.extraction_id] = { ...r }; });
        setOriginalRecords(originals);
        if (onCountChange) onCountChange(sorted.length);
      }
    } catch (err) {
      console.error('Error fetching records:', err);
    } finally {
      setRefreshing(false);
    }
  };

  // --- List handlers ---
  const handleRecordSelect = (id) => {
    setSelectedRecords(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const handleSelectAll = () => {
    setSelectedRecords(prev => prev.length === records.length ? [] : records.map(r => r.extraction_id));
  };

  const handleEditRecord = (record) => {
    setEditingRecord(record.extraction_id);
    setEditValues(record);
  };

  const handleSaveEdit = () => {
    setRecords(prev => prev.map(r => r.extraction_id === editingRecord ? editValues : r));
    setEditingRecord(null);
  };

  const handleCancelEdit = () => {
    setEditingRecord(null);
    setEditValues({});
  };

  const handleFieldChange = (field, value) => {
    setEditValues(prev => ({ ...prev, [field]: value }));
  };

  const handleOpenValidation = (record) => {
    setActiveRecord(record);
    setView('validation');
  };

  const handleValidateSelected = async () => {
    if (selectedRecords.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one record to validate' });
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const recordsToValidate = selectedRecords.map(id => {
        const record = records.find(r => r.extraction_id === id);
        const original = originalRecords[id] || {};
        const updates = {};
        Object.keys(record).forEach(key => {
          if (record[key] !== original[key] && key !== 'extraction_id') updates[key] = record[key];
        });
        return { extraction_id: id, updates };
      });

      const response = await fetch('/api/records/validate-multiple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ records: recordsToValidate })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Failed to validate records');

      setMessage({ type: 'success', text: `Successfully validated ${selectedRecords.length} record(s)!` });
      setSelectedRecords([]);
      setTimeout(() => { fetchRecords(); setMessage(null); }, 2000);
    } catch (err) {
      setMessage({ type: 'error', text: `Failed to validate: ${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedRecords.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one record to delete' });
      return;
    }
    if (!window.confirm(`Are you sure you want to delete ${selectedRecords.length} record(s)?`)) return;

    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch('/api/records/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ extraction_ids: selectedRecords })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Failed to delete records');

      setMessage({ type: 'success', text: `Successfully deleted ${selectedRecords.length} record(s)!` });
      setSelectedRecords([]);
      setTimeout(() => { fetchRecords(); setMessage(null); }, 2000);
    } catch (err) {
      setMessage({ type: 'error', text: `Failed to delete: ${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  // --- Validation flow ---
  const handleValidationComplete = async (validatedData) => {
    try {
      const response = await fetch('/api/validate-record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          extraction_id: activeRecord.extraction_id,
          updates: validatedData
        })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Validation failed');

      setValidatedLeaseData({ ...activeRecord, ...validatedData });
      setView('enrichment');
    } catch (err) {
      setMessage({ type: 'error', text: `Failed to save validation: ${err.message}` });
      setView('list');
    }
  };

  const handleEnrichmentComplete = () => {
    setView('list');
    setActiveRecord(null);
    setValidatedLeaseData(null);
    fetchRecords();
  };

  const handleSkipEnrichment = () => {
    setView('list');
    setActiveRecord(null);
    setValidatedLeaseData(null);
    fetchRecords();
  };

  const handleBackToList = () => {
    setView('list');
    setActiveRecord(null);
    setValidatedLeaseData(null);
  };

  // --- Render ---
  if (view === 'validation' && activeRecord) {
    return (
      <div className="pending-reviews-content">
        <button className="back-to-list-btn" onClick={handleBackToList}>
          <FiArrowLeft size={18} /> Back to Pending Reviews
        </button>
        <ValidationForm
          record={activeRecord}
          onSubmit={handleValidationComplete}
          onCancel={handleBackToList}
        />
      </div>
    );
  }

  if (view === 'enrichment' && validatedLeaseData) {
    return (
      <div className="pending-reviews-content">
        <button className="back-to-list-btn" onClick={handleBackToList}>
          <FiArrowLeft size={18} /> Back to Pending Reviews
        </button>
        <EnrichmentValidation
          leaseRecord={validatedLeaseData}
          onComplete={handleEnrichmentComplete}
          onCancel={handleSkipEnrichment}
        />
      </div>
    );
  }

  return (
    <div className="pending-reviews-content">
        <motion.div
          className="validation-section"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="validation-header">
            <h2 className="validation-title">
              {records.length > 0 ? `${records.length} Record${records.length !== 1 ? 's' : ''} Awaiting Review` : 'No Pending Records'}
            </h2>
            <button
              className="refresh-records-button"
              onClick={fetchRecords}
              disabled={refreshing}
            >
              <FiRefreshCw className={refreshing ? 'spinning' : ''} size={18} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>

          {message && (
            <motion.div
              className={`validation-message ${message.type}`}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
            >
              {message.type === 'success' ? <FiCheck size={20} /> : <FiX size={20} />}
              {message.text}
            </motion.div>
          )}

          {records.length === 0 ? (
            <div className="no-records">
              <FiInbox size={48} />
              <p>No records pending review. Upload a new lease document to get started.</p>
            </div>
          ) : (
            <>
              <div className="validation-actions">
                <button className="select-all-btn" onClick={handleSelectAll}>
                  {selectedRecords.length === records.length ? 'Deselect All' : 'Select All'}
                </button>
                <button
                  className="delete-btn"
                  onClick={handleDeleteSelected}
                  disabled={selectedRecords.length === 0 || loading}
                >
                  <FiTrash2 size={16} />
                  {loading ? 'Deleting...' : `Delete Selected (${selectedRecords.length})`}
                </button>
                <button
                  className="validate-btn"
                  onClick={handleValidateSelected}
                  disabled={selectedRecords.length === 0 || loading}
                >
                  {loading ? 'Validating...' : `Quick Validate (${selectedRecords.length})`}
                </button>
              </div>

              <div className="records-table">
                <table>
                  <thead>
                    <tr>
                      <th><input type="checkbox" checked={selectedRecords.length === records.length && records.length > 0} onChange={handleSelectAll} /></th>
                      <th>Upload Date</th>
                      <th>Tenant</th>
                      <th>Landlord</th>
                      <th>City</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Sq Ft</th>
                      <th>Rent PSF</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map(record => (
                      <tr key={record.extraction_id} className={editingRecord === record.extraction_id ? 'editing' : ''}>
                        <td>
                          <input
                            type="checkbox"
                            checked={selectedRecords.includes(record.extraction_id)}
                            onChange={() => handleRecordSelect(record.extraction_id)}
                            disabled={editingRecord === record.extraction_id}
                          />
                        </td>
                        <td>{record.uploaded_at ? new Date(record.uploaded_at).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true }) : '-'}</td>
                        <td>
                          {editingRecord === record.extraction_id
                            ? <input type="text" value={editValues.tenant_name || ''} onChange={(e) => handleFieldChange('tenant_name', e.target.value)} />
                            : record.tenant_name || '-'}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id
                            ? <input type="text" value={editValues.landlord_name || ''} onChange={(e) => handleFieldChange('landlord_name', e.target.value)} />
                            : record.landlord_name || '-'}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id
                            ? <input type="text" value={editValues.property_city || ''} onChange={(e) => handleFieldChange('property_city', e.target.value)} />
                            : record.property_city || '-'}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id
                            ? <input type="date" value={editValues.commencement_date || ''} onChange={(e) => handleFieldChange('commencement_date', e.target.value)} />
                            : record.commencement_date || '-'}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id
                            ? <input type="date" value={editValues.expiration_date || ''} onChange={(e) => handleFieldChange('expiration_date', e.target.value)} />
                            : record.expiration_date || '-'}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id
                            ? <input type="number" value={editValues.rentable_square_feet || ''} onChange={(e) => handleFieldChange('rentable_square_feet', e.target.value)} />
                            : record.rentable_square_feet ? Number(record.rentable_square_feet).toLocaleString() : '-'}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id
                            ? <input type="number" step="0.01" value={editValues.base_rent_psf || ''} onChange={(e) => handleFieldChange('base_rent_psf', e.target.value)} />
                            : record.base_rent_psf ? `$${Number(record.base_rent_psf).toFixed(2)}` : '-'}
                        </td>
                        <td>
                          {editingRecord === record.extraction_id ? (
                            <div className="edit-actions">
                              <button onClick={handleSaveEdit} className="save-btn" title="Save"><FiSave size={16} /></button>
                              <button onClick={handleCancelEdit} className="cancel-btn" title="Cancel"><FiX size={16} /></button>
                            </div>
                          ) : (
                            <div className="edit-actions">
                              <button onClick={() => handleOpenValidation(record)} className="review-btn" title="Full Review">
                                <FiCheck size={16} /> Review
                              </button>
                              <button onClick={() => handleEditRecord(record)} className="edit-btn" title="Quick Edit">
                                <FiEdit2 size={16} />
                              </button>
                            </div>
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
  );
};

export default PendingReviews;
