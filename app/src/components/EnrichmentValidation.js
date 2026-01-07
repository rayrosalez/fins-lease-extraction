import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FiHome, FiUser, FiTrendingUp, FiDollarSign, FiShield, 
  FiActivity, FiCheckCircle, FiAlertTriangle, FiEdit3, 
  FiSave, FiRefreshCw, FiX, FiBriefcase, FiMapPin, FiUsers
} from 'react-icons/fi';
import './EnrichmentValidation.css';

const API_BASE_URL = '/api';

const EnrichmentValidation = ({ leaseRecord, onComplete, onCancel }) => {
  const [enrichmentStage, setEnrichmentStage] = useState('idle'); // idle, enriching, review, saving, complete
  const [landlordData, setLandlordData] = useState(null);
  const [tenantData, setTenantData] = useState(null);
  const [editingLandlord, setEditingLandlord] = useState(false);
  const [editingTenant, setEditingTenant] = useState(false);
  const [editedLandlord, setEditedLandlord] = useState({});
  const [editedTenant, setEditedTenant] = useState({});
  const [error, setError] = useState(null);
  const [saveProgress, setSaveProgress] = useState({ landlord: null, tenant: null });

  // Start enrichment automatically when component mounts
  useEffect(() => {
    if (leaseRecord && enrichmentStage === 'idle') {
      startEnrichment();
    }
  }, [leaseRecord]);

  const startEnrichment = async () => {
    setEnrichmentStage('enriching');
    setError(null);
    
    try {
      const results = { landlord: null, tenant: null };
      
      // Enrich landlord
      if (leaseRecord.landlord_name) {
        const landlordRes = await fetch(`${API_BASE_URL}/enrich/landlord`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            landlord_name: leaseRecord.landlord_name,
            landlord_address: leaseRecord.landlord_address || ''
          })
        });
        const landlordData = await landlordRes.json();
        if (landlordRes.ok) {
          results.landlord = landlordData;
          setLandlordData(landlordData);
          setEditedLandlord(landlordData.enriched_data || {});
        }
      }
      
      // Enrich tenant
      if (leaseRecord.tenant_name) {
        const tenantRes = await fetch(`${API_BASE_URL}/enrich/tenant`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tenant_name: leaseRecord.tenant_name,
            tenant_address: leaseRecord.tenant_address || '',
            industry_sector: leaseRecord.industry_sector || ''
          })
        });
        const tenantData = await tenantRes.json();
        if (tenantRes.ok) {
          results.tenant = tenantData;
          setTenantData(tenantData);
          setEditedTenant(tenantData.enriched_data || {});
        }
      }
      
      setEnrichmentStage('review');
    } catch (err) {
      console.error('Enrichment error:', err);
      setError(err.message);
      setEnrichmentStage('idle');
    }
  };

  const handleSaveEnrichment = async () => {
    setEnrichmentStage('saving');
    setSaveProgress({ landlord: 'saving', tenant: 'saving' });
    
    try {
      // Save landlord
      if (landlordData && !landlordData.already_exists) {
        const landlordRes = await fetch(`${API_BASE_URL}/enrich/validate-landlord`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            landlord_id: landlordData.landlord_id,
            landlord_name: landlordData.landlord_name,
            landlord_address: landlordData.landlord_address,
            enriched_data: editedLandlord
          })
        });
        
        if (landlordRes.ok) {
          setSaveProgress(prev => ({ ...prev, landlord: 'success' }));
        } else {
          const err = await landlordRes.json();
          setSaveProgress(prev => ({ ...prev, landlord: 'error' }));
          throw new Error(err.error);
        }
      } else {
        setSaveProgress(prev => ({ ...prev, landlord: 'skipped' }));
      }
      
      // Save tenant
      if (tenantData && !tenantData.already_exists) {
        const tenantRes = await fetch(`${API_BASE_URL}/enrich/validate-tenant`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tenant_id: tenantData.tenant_id,
            tenant_name: tenantData.tenant_name,
            tenant_address: tenantData.tenant_address,
            industry_sector: tenantData.industry_sector,
            enriched_data: editedTenant
          })
        });
        
        if (tenantRes.ok) {
          setSaveProgress(prev => ({ ...prev, tenant: 'success' }));
        } else {
          const err = await tenantRes.json();
          setSaveProgress(prev => ({ ...prev, tenant: 'error' }));
          throw new Error(err.error);
        }
      } else {
        setSaveProgress(prev => ({ ...prev, tenant: 'skipped' }));
      }
      
      setEnrichmentStage('complete');
      setTimeout(() => {
        onComplete && onComplete();
      }, 2000);
      
    } catch (err) {
      console.error('Save error:', err);
      setError(err.message);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const getRiskColor = (risk) => {
    switch (risk?.toUpperCase()) {
      case 'LOW': return '#10B981';
      case 'MEDIUM': return '#F59E0B';
      case 'HIGH': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toUpperCase()) {
      case 'POSITIVE': return '#10B981';
      case 'NEUTRAL': return '#6B7280';
      case 'NEGATIVE': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const renderEnrichingState = () => (
    <motion.div 
      className="enrichment-loading-state"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="loading-animation">
        <div className="loading-circle"></div>
        <div className="loading-circle"></div>
        <div className="loading-circle"></div>
      </div>
      <h3>AI Enrichment in Progress</h3>
      <p>Claude AI is searching for financial information about:</p>
      <div className="enriching-entities">
        {leaseRecord.landlord_name && (
          <div className="enriching-entity">
            <FiHome size={20} />
            <span>{leaseRecord.landlord_name}</span>
          </div>
        )}
        {leaseRecord.tenant_name && (
          <div className="enriching-entity">
            <FiUser size={20} />
            <span>{leaseRecord.tenant_name}</span>
          </div>
        )}
      </div>
    </motion.div>
  );

  const renderLandlordCard = () => {
    if (!landlordData) return null;
    
    const data = editedLandlord;
    const isExisting = landlordData.already_exists;
    
    return (
      <motion.div 
        className={`enrichment-card landlord-card ${isExisting ? 'existing' : ''}`}
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="card-header">
          <div className="card-title">
            <FiHome className="card-icon" size={24} />
            <div>
              <h3>Landlord Profile</h3>
              <p className="entity-name">{landlordData.landlord_name}</p>
            </div>
          </div>
          {isExisting ? (
            <span className="status-badge existing">Already Enriched</span>
          ) : (
            <button 
              className="edit-btn"
              onClick={() => setEditingLandlord(!editingLandlord)}
            >
              <FiEdit3 size={16} />
              {editingLandlord ? 'Done' : 'Edit'}
            </button>
          )}
        </div>
        
        {!isExisting && (
          <div className="card-content">
            <div className="info-grid">
              <div className="info-item">
                <label>Company Type</label>
                {editingLandlord ? (
                  <input 
                    value={data.company_type || ''} 
                    onChange={(e) => setEditedLandlord({...data, company_type: e.target.value})}
                  />
                ) : (
                  <span>{data.company_type || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Stock Ticker</label>
                {editingLandlord ? (
                  <input 
                    value={data.stock_ticker || ''} 
                    onChange={(e) => setEditedLandlord({...data, stock_ticker: e.target.value})}
                  />
                ) : (
                  <span>{data.stock_ticker || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Market Cap</label>
                {editingLandlord ? (
                  <input 
                    type="number"
                    value={data.market_cap || ''} 
                    onChange={(e) => setEditedLandlord({...data, market_cap: parseFloat(e.target.value)})}
                  />
                ) : (
                  <span>{formatCurrency(data.market_cap)}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Annual Revenue</label>
                {editingLandlord ? (
                  <input 
                    type="number"
                    value={data.annual_revenue || ''} 
                    onChange={(e) => setEditedLandlord({...data, annual_revenue: parseFloat(e.target.value)})}
                  />
                ) : (
                  <span>{formatCurrency(data.annual_revenue)}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Credit Rating</label>
                {editingLandlord ? (
                  <input 
                    value={data.credit_rating || ''} 
                    onChange={(e) => setEditedLandlord({...data, credit_rating: e.target.value})}
                  />
                ) : (
                  <span>{data.credit_rating || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Total Properties</label>
                {editingLandlord ? (
                  <input 
                    type="number"
                    value={data.total_properties || ''} 
                    onChange={(e) => setEditedLandlord({...data, total_properties: parseInt(e.target.value)})}
                  />
                ) : (
                  <span>{data.total_properties || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Property Types</label>
                {editingLandlord ? (
                  <input 
                    value={data.primary_property_types || ''} 
                    onChange={(e) => setEditedLandlord({...data, primary_property_types: e.target.value})}
                  />
                ) : (
                  <span>{data.primary_property_types || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Geographic Focus</label>
                {editingLandlord ? (
                  <input 
                    value={data.geographic_focus || ''} 
                    onChange={(e) => setEditedLandlord({...data, geographic_focus: e.target.value})}
                  />
                ) : (
                  <span>{data.geographic_focus || '-'}</span>
                )}
              </div>
            </div>
            
            <div className="risk-indicators">
              <div className="risk-item">
                <label>Financial Health</label>
                <div className="health-score">
                  <div 
                    className="score-bar"
                    style={{ width: `${(data.financial_health_score || 5) * 10}%` }}
                  ></div>
                  <span>{data.financial_health_score || 5}/10</span>
                </div>
              </div>
              
              <div className="risk-item">
                <label>Bankruptcy Risk</label>
                <span 
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(data.bankruptcy_risk) }}
                >
                  {data.bankruptcy_risk || 'MEDIUM'}
                </span>
              </div>
              
              <div className="risk-item">
                <label>News Sentiment</label>
                <span 
                  className="sentiment-badge"
                  style={{ backgroundColor: getSentimentColor(data.recent_news_sentiment) }}
                >
                  {data.recent_news_sentiment || 'NEUTRAL'}
                </span>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    );
  };

  const renderTenantCard = () => {
    if (!tenantData) return null;
    
    const data = editedTenant;
    const isExisting = tenantData.already_exists;
    
    return (
      <motion.div 
        className={`enrichment-card tenant-card ${isExisting ? 'existing' : ''}`}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="card-header">
          <div className="card-title">
            <FiUser className="card-icon" size={24} />
            <div>
              <h3>Tenant Profile</h3>
              <p className="entity-name">{tenantData.tenant_name}</p>
            </div>
          </div>
          {isExisting ? (
            <span className="status-badge existing">Already Enriched</span>
          ) : (
            <button 
              className="edit-btn"
              onClick={() => setEditingTenant(!editingTenant)}
            >
              <FiEdit3 size={16} />
              {editingTenant ? 'Done' : 'Edit'}
            </button>
          )}
        </div>
        
        {!isExisting && (
          <div className="card-content">
            <div className="info-grid">
              <div className="info-item">
                <label>Company Type</label>
                {editingTenant ? (
                  <input 
                    value={data.company_type || ''} 
                    onChange={(e) => setEditedTenant({...data, company_type: e.target.value})}
                  />
                ) : (
                  <span>{data.company_type || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Stock Ticker</label>
                {editingTenant ? (
                  <input 
                    value={data.stock_ticker || ''} 
                    onChange={(e) => setEditedTenant({...data, stock_ticker: e.target.value})}
                  />
                ) : (
                  <span>{data.stock_ticker || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Industry</label>
                <span>{tenantData.industry_sector || '-'}</span>
              </div>
              
              <div className="info-item">
                <label>Headquarters</label>
                {editingTenant ? (
                  <input 
                    value={data.headquarters_location || ''} 
                    onChange={(e) => setEditedTenant({...data, headquarters_location: e.target.value})}
                  />
                ) : (
                  <span>{data.headquarters_location || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Annual Revenue</label>
                {editingTenant ? (
                  <input 
                    type="number"
                    value={data.annual_revenue || ''} 
                    onChange={(e) => setEditedTenant({...data, annual_revenue: parseFloat(e.target.value)})}
                  />
                ) : (
                  <span>{formatCurrency(data.annual_revenue)}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Employee Count</label>
                {editingTenant ? (
                  <input 
                    type="number"
                    value={data.employee_count || ''} 
                    onChange={(e) => setEditedTenant({...data, employee_count: parseInt(e.target.value)})}
                  />
                ) : (
                  <span>{data.employee_count?.toLocaleString() || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Credit Rating</label>
                {editingTenant ? (
                  <input 
                    value={data.credit_rating || ''} 
                    onChange={(e) => setEditedTenant({...data, credit_rating: e.target.value})}
                  />
                ) : (
                  <span>{data.credit_rating || '-'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Years in Business</label>
                {editingTenant ? (
                  <input 
                    type="number"
                    value={data.years_in_business || ''} 
                    onChange={(e) => setEditedTenant({...data, years_in_business: parseInt(e.target.value)})}
                  />
                ) : (
                  <span>{data.years_in_business || '-'}</span>
                )}
              </div>
            </div>
            
            <div className="risk-indicators">
              <div className="risk-item">
                <label>Financial Health</label>
                <div className="health-score">
                  <div 
                    className="score-bar"
                    style={{ width: `${(data.financial_health_score || 5) * 10}%` }}
                  ></div>
                  <span>{data.financial_health_score || 5}/10</span>
                </div>
              </div>
              
              <div className="risk-item">
                <label>Bankruptcy Risk</label>
                <span 
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(data.bankruptcy_risk) }}
                >
                  {data.bankruptcy_risk || 'MEDIUM'}
                </span>
              </div>
              
              <div className="risk-item">
                <label>Industry Risk</label>
                <span 
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(data.industry_risk) }}
                >
                  {data.industry_risk || 'MEDIUM'}
                </span>
              </div>
              
              <div className="risk-item">
                <label>News Sentiment</label>
                <span 
                  className="sentiment-badge"
                  style={{ backgroundColor: getSentimentColor(data.recent_news_sentiment) }}
                >
                  {data.recent_news_sentiment || 'NEUTRAL'}
                </span>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    );
  };

  const renderCompleteState = () => (
    <motion.div 
      className="enrichment-complete-state"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <div className="complete-icon">
        <FiCheckCircle size={64} color="#10B981" />
      </div>
      <h3>Enrichment Complete!</h3>
      <p>Financial profiles have been saved successfully.</p>
      <div className="save-results">
        {saveProgress.landlord && (
          <div className={`save-result ${saveProgress.landlord}`}>
            <FiHome size={18} />
            <span>Landlord: {saveProgress.landlord === 'success' ? 'Saved' : saveProgress.landlord === 'skipped' ? 'Already exists' : 'Error'}</span>
          </div>
        )}
        {saveProgress.tenant && (
          <div className={`save-result ${saveProgress.tenant}`}>
            <FiUser size={18} />
            <span>Tenant: {saveProgress.tenant === 'success' ? 'Saved' : saveProgress.tenant === 'skipped' ? 'Already exists' : 'Error'}</span>
          </div>
        )}
      </div>
    </motion.div>
  );

  return (
    <motion.div 
      className="enrichment-validation-container"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="enrichment-header">
        <div className="header-icon">
          <FiTrendingUp size={48} color="#00A67E" />
        </div>
        <h2 className="enrichment-title">AI Enrichment Validation</h2>
        <p className="enrichment-subtitle">
          Review and validate the financial profiles before saving to the database
        </p>
      </div>

      {error && (
        <div className="enrichment-error">
          <FiAlertTriangle size={20} />
          <span>{error}</span>
          <button onClick={() => setError(null)}>
            <FiX size={16} />
          </button>
        </div>
      )}

      {enrichmentStage === 'enriching' && renderEnrichingState()}
      
      {enrichmentStage === 'complete' && renderCompleteState()}

      {enrichmentStage === 'review' && (
        <>
          <div className="enrichment-cards">
            {renderLandlordCard()}
            {renderTenantCard()}
          </div>

          <div className="enrichment-actions">
            <button className="skip-btn" onClick={onCancel}>
              <FiX size={18} />
              Skip Enrichment
            </button>
            <button className="retry-btn" onClick={startEnrichment}>
              <FiRefreshCw size={18} />
              Re-enrich
            </button>
            <button className="save-btn" onClick={handleSaveEnrichment}>
              <FiSave size={18} />
              Save Profiles
            </button>
          </div>
        </>
      )}

      {enrichmentStage === 'saving' && (
        <div className="saving-overlay">
          <div className="saving-spinner"></div>
          <p>Saving enrichment data...</p>
        </div>
      )}
    </motion.div>
  );
};

export default EnrichmentValidation;

