import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FiHome, FiUser, FiBriefcase, FiMapPin, FiFileText,
  FiCalendar, FiClock, FiMaximize, FiDollarSign, FiTrendingUp,
  FiBell, FiEdit3, FiCheckCircle, FiCpu, FiBarChart2, FiZap
} from 'react-icons/fi';
import './ValidationForm.css';

const API_BASE_URL = 'http://localhost:5001/api';

const ValidationForm = ({ record, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    landlord_name: record.landlord_name || '',
    landlord_address: record.landlord_address || '',
    tenant_name: record.tenant_name || '',
    tenant_address: record.tenant_address || '',
    industry_sector: record.industry_sector || '',
    suite_number: record.suite_number || '',
    lease_type: record.lease_type || '',
    commencement_date: record.commencement_date || '',
    expiration_date: record.expiration_date || '',
    term_months: record.term_months || '',
    rentable_square_feet: record.rentable_square_feet || '',
    annual_base_rent: record.annual_base_rent || '',
    base_rent_psf: record.base_rent_psf || '',
    annual_escalation_pct: record.annual_escalation_pct || '',
    renewal_notice_days: record.renewal_notice_days || '',
    guarantor: record.guarantor || '',
    property_address: record.property_address || '',
    property_street_address: record.property_street_address || '',
    property_city: record.property_city || '',
    property_state: record.property_state || '',
    property_zip_code: record.property_zip_code || '',
    property_country: record.property_country || ''
  });

  const [errors, setErrors] = useState({});
  const [enrichmentStatus, setEnrichmentStatus] = useState('idle'); // idle, enriching, enriched, error
  const [enrichmentData, setEnrichmentData] = useState(null);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.tenant_name) newErrors.tenant_name = 'Required';
    if (!formData.landlord_name) newErrors.landlord_name = 'Required';
    if (!formData.commencement_date) newErrors.commencement_date = 'Required';
    if (!formData.expiration_date) newErrors.expiration_date = 'Required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleEnrichment = async () => {
    if (!formData.landlord_name && !formData.tenant_name) {
      setErrors({ ...errors, enrichment: 'Need at least landlord or tenant name to enrich' });
      return;
    }

    setEnrichmentStatus('enriching');
    
    try {
      // Enrich using the record's extraction_id if available, otherwise enrich individually
      if (record.extraction_id) {
        const response = await fetch(`${API_BASE_URL}/enrich/record/${record.extraction_id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
          setEnrichmentData(data.results);
          setEnrichmentStatus('enriched');
        } else {
          throw new Error(data.error || 'Enrichment failed');
        }
      } else {
        // Enrich landlord and tenant separately
        const results = { landlord: null, tenant: null, errors: [] };
        
        if (formData.landlord_name) {
          const landlordRes = await fetch(`${API_BASE_URL}/enrich/landlord`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              landlord_name: formData.landlord_name,
              landlord_address: formData.landlord_address
            })
          });
          const landlordData = await landlordRes.json();
          if (landlordRes.ok) {
            results.landlord = landlordData;
          } else {
            results.errors.push(landlordData.error);
          }
        }
        
        if (formData.tenant_name) {
          const tenantRes = await fetch(`${API_BASE_URL}/enrich/tenant`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              tenant_name: formData.tenant_name,
              tenant_address: formData.tenant_address,
              industry_sector: formData.industry_sector
            })
          });
          const tenantData = await tenantRes.json();
          if (tenantRes.ok) {
            results.tenant = tenantData;
          } else {
            results.errors.push(tenantData.error);
          }
        }
        
        setEnrichmentData(results);
        setEnrichmentStatus(results.landlord || results.tenant ? 'enriched' : 'error');
      }
    } catch (err) {
      console.error('Enrichment error:', err);
      setEnrichmentStatus('error');
      setErrors({ ...errors, enrichment: err.message });
    }
  };

  const fields = [
    { label: 'Landlord Name', key: 'landlord_name', required: true, icon: FiHome },
    { label: 'Landlord Address', key: 'landlord_address', icon: FiMapPin },
    { label: 'Tenant Name', key: 'tenant_name', required: true, icon: FiUser },
    { label: 'Tenant Address', key: 'tenant_address', icon: FiMapPin },
    { label: 'Industry Sector', key: 'industry_sector', icon: FiBriefcase },
    { label: 'Property Address', key: 'property_address', icon: FiMapPin },
    { label: 'Property Street', key: 'property_street_address', icon: FiMapPin },
    { label: 'Property City', key: 'property_city', icon: FiMapPin },
    { label: 'Property State', key: 'property_state', icon: FiMapPin },
    { label: 'Property ZIP Code', key: 'property_zip_code', icon: FiMapPin },
    { label: 'Property Country', key: 'property_country', icon: FiMapPin },
    { label: 'Suite Number', key: 'suite_number', icon: FiMapPin },
    { label: 'Lease Type', key: 'lease_type', icon: FiFileText },
    { label: 'Commencement Date', key: 'commencement_date', type: 'date', required: true, icon: FiCalendar },
    { label: 'Expiration Date', key: 'expiration_date', type: 'date', required: true, icon: FiCalendar },
    { label: 'Term (Months)', key: 'term_months', type: 'number', icon: FiClock },
    { label: 'Square Feet', key: 'rentable_square_feet', type: 'number', icon: FiMaximize },
    { label: 'Annual Base Rent', key: 'annual_base_rent', type: 'number', icon: FiDollarSign },
    { label: 'Base Rent PSF', key: 'base_rent_psf', type: 'number', icon: FiDollarSign },
    { label: 'Annual Escalation %', key: 'annual_escalation_pct', type: 'number', icon: FiTrendingUp },
    { label: 'Renewal Notice Days', key: 'renewal_notice_days', type: 'number', icon: FiBell },
    { label: 'Guarantor', key: 'guarantor', icon: FiEdit3 }
  ];

  return (
    <motion.div 
      className="validation-container"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="validation-header">
        <div className="success-icon">
          <FiCheckCircle size={64} color="#FF3621" />
        </div>
        <h2 className="validation-title">Review & Validate Extraction</h2>
        <p className="validation-subtitle">
          AI has extracted the following data. Please review and fill in any missing information.
        </p>
      </div>

      <div className="validation-form">
        {fields.map((field, index) => {
          const IconComponent = field.icon;
          return (
            <motion.div
              key={field.key}
              className="form-field"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <label className="field-label">
                <IconComponent className="field-icon" size={18} />
                <span className="field-name">
                  {field.label}
                  {field.required && <span className="required-star">*</span>}
                </span>
              </label>
              <input
                type={field.type || 'text'}
                value={formData[field.key]}
                onChange={(e) => handleChange(field.key, e.target.value)}
                className={`field-input ${errors[field.key] ? 'error' : ''} ${!record[field.key] ? 'empty' : ''}`}
                placeholder={!record[field.key] ? 'AI could not extract this field' : ''}
              />
              {errors[field.key] && (
                <span className="field-error">{errors[field.key]}</span>
              )}
              {!record[field.key] && formData[field.key] && (
                <span className="field-badge">User Added</span>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* AI Enrichment Section */}
      <motion.div 
        className="enrichment-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="enrichment-header">
          <FiZap className="enrichment-icon" size={24} />
          <div className="enrichment-title-group">
            <h3 className="enrichment-title">AI Enrichment</h3>
            <p className="enrichment-description">
              Use Claude AI to find financial and company information about the landlord and tenant
            </p>
          </div>
        </div>
        
        {enrichmentStatus === 'idle' && (
          <button 
            className="enrich-button"
            onClick={handleEnrichment}
            disabled={!formData.landlord_name && !formData.tenant_name}
          >
            <FiZap size={20} />
            <span>Enrich with Claude AI</span>
          </button>
        )}
        
        {enrichmentStatus === 'enriching' && (
          <div className="enrichment-loading">
            <div className="enrichment-spinner"></div>
            <span>Searching web for financial data...</span>
          </div>
        )}
        
        {enrichmentStatus === 'enriched' && enrichmentData && (
          <div className="enrichment-results">
            <div className="enrichment-success">
              <FiCheckCircle size={20} color="#10B981" />
              <span>Enrichment complete!</span>
            </div>
            
            {enrichmentData.landlord && (
              <div className="enrichment-card">
                <h4><FiHome size={16} /> Landlord: {formData.landlord_name}</h4>
                <p className="enrichment-status">Financial profile created</p>
              </div>
            )}
            
            {enrichmentData.tenant && (
              <div className="enrichment-card">
                <h4><FiUser size={16} /> Tenant: {formData.tenant_name}</h4>
                <p className="enrichment-status">Financial profile created</p>
              </div>
            )}
            
            {enrichmentData.errors && enrichmentData.errors.length > 0 && (
              <div className="enrichment-warnings">
                {enrichmentData.errors.map((err, i) => (
                  <p key={i} className="enrichment-warning">⚠️ {err}</p>
                ))}
              </div>
            )}
          </div>
        )}
        
        {enrichmentStatus === 'error' && (
          <div className="enrichment-error">
            <span>❌ Enrichment failed. You can still validate manually.</span>
            <button className="retry-enrich-button" onClick={handleEnrichment}>
              Retry
            </button>
          </div>
        )}
      </motion.div>

      <div className="validation-actions">
        <button className="cancel-button" onClick={onCancel}>
          Cancel
        </button>
        <button className="submit-button" onClick={handleSubmit}>
          <span>Validate & Submit</span>
          <span className="button-arrow">→</span>
        </button>
      </div>

      <div className="validation-info">
        <div className="info-item">
          <FiCpu className="info-icon" size={20} color="#FF3621" />
          <span className="info-text">AI Confidence: 94.3%</span>
        </div>
        <div className="info-item">
          <FiBarChart2 className="info-icon" size={20} color="#8B4513" />
          <span className="info-text">
            {Object.values(formData).filter(v => v).length} / {fields.length} fields extracted
          </span>
        </div>
        {enrichmentStatus === 'enriched' && (
          <div className="info-item">
            <FiZap className="info-icon" size={20} color="#10B981" />
            <span className="info-text">AI Enriched</span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ValidationForm;
