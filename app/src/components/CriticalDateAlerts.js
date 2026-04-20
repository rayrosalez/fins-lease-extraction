import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiAlertTriangle, FiClock, FiDollarSign, FiChevronDown, FiChevronUp,
  FiCalendar, FiRefreshCw, FiFilter, FiBell, FiAlertCircle,
  FiMapPin, FiUser, FiFileText
} from 'react-icons/fi';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie, Legend
} from 'recharts';
import './CriticalDateAlerts.css';

const API_BASE_URL = '/api';

const TIER_CONFIG = {
  EXPIRED: { color: '#6B7280', label: 'Expired', icon: FiAlertCircle, priority: 0 },
  CRITICAL: { color: '#EF4444', label: 'Critical (< 90 days)', icon: FiAlertTriangle, priority: 1 },
  URGENT: { color: '#F59E0B', label: 'Urgent (90-180 days)', icon: FiBell, priority: 2 },
  UPCOMING: { color: '#3B82F6', label: 'Upcoming (180-365 days)', icon: FiClock, priority: 3 },
};

const formatCurrency = (value) => {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const CriticalDateAlerts = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterTier, setFilterTier] = useState('all');
  const [expandedLease, setExpandedLease] = useState(null);
  const [sortKey, setSortKey] = useState('days_to_expiry');
  const [sortDir, setSortDir] = useState('asc');

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/alerts/critical-dates`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      } else {
        const errorText = await response.text();
        setError(`Failed to fetch alerts (${response.status}): ${errorText}`);
      }
      setLoading(false);
    } catch (err) {
      setError(`Failed to connect to backend: ${err.message}`);
      setLoading(false);
    }
  };

  const filteredAlerts = useMemo(() => {
    if (!data?.alerts) return [];
    let alerts = filterTier === 'all'
      ? data.alerts
      : data.alerts.filter(a => a.alert_tier === filterTier);

    alerts = [...alerts].sort((a, b) => {
      let aVal = a[sortKey];
      let bVal = b[sortKey];
      if (typeof aVal === 'string') aVal = aVal?.toLowerCase() || '';
      if (typeof bVal === 'string') bVal = bVal?.toLowerCase() || '';
      if (sortDir === 'asc') return aVal > bVal ? 1 : -1;
      return aVal < bVal ? 1 : -1;
    });

    return alerts;
  }, [data, filterTier, sortKey, sortDir]);

  const pieData = useMemo(() => {
    if (!data?.summary) return [];
    return Object.entries(data.summary)
      .filter(([, count]) => count > 0)
      .map(([tier, count]) => ({
        name: TIER_CONFIG[tier]?.label || tier,
        value: count,
        color: TIER_CONFIG[tier]?.color || '#6B7280',
      }));
  }, [data]);

  const timelineData = useMemo(() => {
    if (!data?.alerts) return [];
    const months = {};
    data.alerts.forEach(a => {
      if (!a.lease_end_date) return;
      const d = new Date(a.lease_end_date);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      const label = d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
      if (!months[key]) months[key] = { month: label, count: 0, revenue: 0 };
      months[key].count += 1;
      months[key].revenue += a.estimated_annual_rent || 0;
    });
    return Object.entries(months)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([, v]) => v);
  }, [data]);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  if (loading) {
    return (
      <div className="alerts-page">
        <div className="alerts-container">
          <div className="loading-container">
            <div className="loading-spinner" />
            <p style={{ color: 'rgba(255,255,255,0.7)', marginTop: '1rem' }}>Loading critical date alerts...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alerts-page">
        <div className="alerts-container">
          <div className="error-container">
            <FiAlertTriangle size={48} color="#EF4444" />
            <p style={{ color: '#EF4444', marginTop: '1rem' }}>{error}</p>
            <button className="refresh-button" onClick={fetchAlerts}>
              <FiRefreshCw size={16} /> Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const summary = data?.summary || {};

  return (
    <div className="alerts-page">
      <div className="alerts-container">
        {/* Header */}
        <div className="alerts-header">
          <div>
            <h1 className="alerts-title">Critical Date Alerts</h1>
            <p className="alerts-subtitle">
              Proactive tracking of lease expirations, renewal deadlines, and critical milestones
            </p>
          </div>
          <button className="refresh-button" onClick={fetchAlerts}>
            <FiRefreshCw size={16} /> Refresh
          </button>
        </div>

        {/* Summary Cards */}
        <motion.div
          className="alert-summary-grid"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="summary-card summary-critical">
            <div className="summary-icon-wrap" style={{ background: 'rgba(239,68,68,0.15)' }}>
              <FiAlertTriangle size={24} color="#EF4444" />
            </div>
            <div className="summary-info">
              <span className="summary-value">{summary.CRITICAL || 0}</span>
              <span className="summary-label">Critical (&lt;90d)</span>
            </div>
          </div>

          <div className="summary-card summary-urgent">
            <div className="summary-icon-wrap" style={{ background: 'rgba(245,158,11,0.15)' }}>
              <FiBell size={24} color="#F59E0B" />
            </div>
            <div className="summary-info">
              <span className="summary-value">{summary.URGENT || 0}</span>
              <span className="summary-label">Urgent (90-180d)</span>
            </div>
          </div>

          <div className="summary-card summary-upcoming">
            <div className="summary-icon-wrap" style={{ background: 'rgba(59,130,246,0.15)' }}>
              <FiClock size={24} color="#3B82F6" />
            </div>
            <div className="summary-info">
              <span className="summary-value">{summary.UPCOMING || 0}</span>
              <span className="summary-label">Upcoming (180-365d)</span>
            </div>
          </div>

          <div className="summary-card summary-revenue">
            <div className="summary-icon-wrap" style={{ background: 'rgba(255,54,33,0.15)' }}>
              <FiDollarSign size={24} color="#FF3621" />
            </div>
            <div className="summary-info">
              <span className="summary-value">{formatCurrency(data?.total_revenue_at_risk || 0)}</span>
              <span className="summary-label">Revenue at Risk</span>
            </div>
          </div>
        </motion.div>

        {/* Charts Row */}
        <div className="alerts-charts-row">
          {/* Expiration Timeline */}
          <motion.div
            className="chart-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <h3 className="chart-title">
              <FiCalendar size={18} /> Expiration Timeline
            </h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={timelineData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="month" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }} />
                <YAxis tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(20,20,20,0.95)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                  formatter={(value, name) => [
                    name === 'revenue' ? formatCurrency(value) : value,
                    name === 'revenue' ? 'Annual Revenue' : 'Leases Expiring'
                  ]}
                />
                <Bar dataKey="count" name="count" radius={[4, 4, 0, 0]}>
                  {timelineData.map((entry, i) => (
                    <Cell key={i} fill={i < 3 ? '#EF4444' : i < 6 ? '#F59E0B' : '#3B82F6'} fillOpacity={0.8} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Distribution Pie */}
          <motion.div
            className="chart-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h3 className="chart-title">
              <FiFilter size={18} /> Alert Distribution
            </h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, value }) => `${value}`}
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Legend
                  verticalAlign="bottom"
                  iconType="circle"
                  formatter={(value) => <span style={{ color: 'rgba(255,255,255,0.8)', fontSize: '12px' }}>{value}</span>}
                />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(20,20,20,0.95)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Filter Bar */}
        <div className="alert-filter-bar">
          <div className="filter-group">
            <FiFilter size={16} />
            <button
              className={`filter-chip ${filterTier === 'all' ? 'active' : ''}`}
              onClick={() => setFilterTier('all')}
            >
              All ({data?.total_alerts || 0})
            </button>
            {Object.entries(TIER_CONFIG).map(([tier, config]) => {
              const count = summary[tier] || 0;
              if (count === 0) return null;
              return (
                <button
                  key={tier}
                  className={`filter-chip ${filterTier === tier ? 'active' : ''}`}
                  onClick={() => setFilterTier(tier)}
                  style={{ '--chip-color': config.color }}
                >
                  <span className="chip-dot" style={{ background: config.color }} />
                  {config.label.split(' ')[0]} ({count})
                </button>
              );
            })}
          </div>
        </div>

        {/* Alerts Table */}
        <motion.div
          className="alerts-table-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <table className="alerts-table">
            <thead>
              <tr>
                <th>Status</th>
                <th className="sortable" onClick={() => handleSort('tenant_name')}>
                  Tenant {sortKey === 'tenant_name' && (sortDir === 'asc' ? <FiChevronUp size={14} /> : <FiChevronDown size={14} />)}
                </th>
                <th className="sortable" onClick={() => handleSort('property_id')}>
                  Property {sortKey === 'property_id' && (sortDir === 'asc' ? <FiChevronUp size={14} /> : <FiChevronDown size={14} />)}
                </th>
                <th className="sortable" onClick={() => handleSort('days_to_expiry')}>
                  Days Left {sortKey === 'days_to_expiry' && (sortDir === 'asc' ? <FiChevronUp size={14} /> : <FiChevronDown size={14} />)}
                </th>
                <th>Expiration</th>
                <th className="sortable" onClick={() => handleSort('estimated_annual_rent')}>
                  Annual Rent {sortKey === 'estimated_annual_rent' && (sortDir === 'asc' ? <FiChevronUp size={14} /> : <FiChevronDown size={14} />)}
                </th>
                <th className="sortable" onClick={() => handleSort('risk_score')}>
                  Risk {sortKey === 'risk_score' && (sortDir === 'asc' ? <FiChevronUp size={14} /> : <FiChevronDown size={14} />)}
                </th>
                <th>Notices</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <AnimatePresence>
                {filteredAlerts.map((alert, idx) => {
                  const tierConfig = TIER_CONFIG[alert.alert_tier] || TIER_CONFIG.UPCOMING;
                  const TierIcon = tierConfig.icon;
                  const isExpanded = expandedLease === alert.lease_id;

                  return (
                    <React.Fragment key={alert.lease_id}>
                      <motion.tr
                        className={`alert-row tier-${alert.alert_tier?.toLowerCase()}`}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.02 }}
                        onClick={() => setExpandedLease(isExpanded ? null : alert.lease_id)}
                        style={{ cursor: 'pointer' }}
                      >
                        <td>
                          <span className="tier-badge" style={{ background: `${tierConfig.color}20`, color: tierConfig.color, borderColor: `${tierConfig.color}40` }}>
                            <TierIcon size={14} />
                            {alert.alert_tier}
                          </span>
                        </td>
                        <td className="cell-tenant">
                          <strong>{alert.tenant_name}</strong>
                          <span className="cell-sub">{alert.industry_sector}</span>
                        </td>
                        <td className="cell-property">{alert.property_id || 'N/A'}</td>
                        <td>
                          <span className={`days-badge ${alert.days_to_expiry <= 90 ? 'days-critical' : alert.days_to_expiry <= 180 ? 'days-urgent' : 'days-upcoming'}`}>
                            {alert.days_to_expiry < 0 ? `${Math.abs(alert.days_to_expiry)}d overdue` : `${alert.days_to_expiry}d`}
                          </span>
                        </td>
                        <td>{formatDate(alert.lease_end_date)}</td>
                        <td className="cell-rent">{formatCurrency(alert.estimated_annual_rent)}</td>
                        <td>
                          <div className="risk-bar-mini">
                            <div
                              className="risk-bar-fill"
                              style={{
                                width: `${Math.min(alert.risk_score, 100)}%`,
                                background: alert.risk_score > 70 ? '#EF4444' : alert.risk_score > 40 ? '#F59E0B' : '#10B981',
                              }}
                            />
                          </div>
                          <span className="risk-score-text">{alert.risk_score.toFixed(0)}</span>
                        </td>
                        <td>
                          {alert.notice_deadline_passed && (
                            <span className="notice-warning" title="Renewal notice deadline may have passed">
                              <FiAlertCircle size={16} color="#EF4444" />
                            </span>
                          )}
                        </td>
                        <td>
                          {isExpanded ? <FiChevronUp size={16} /> : <FiChevronDown size={16} />}
                        </td>
                      </motion.tr>

                      {isExpanded && (
                        <tr className="expanded-row">
                          <td colSpan={9}>
                            <motion.div
                              className="expanded-content"
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              transition={{ duration: 0.3 }}
                            >
                              <div className="expanded-grid">
                                <div className="expanded-section">
                                  <h4><FiFileText size={16} /> Lease Details</h4>
                                  <div className="detail-row">
                                    <span className="detail-label">Lease ID</span>
                                    <span className="detail-value">{alert.lease_id}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Lease Type</span>
                                    <span className="detail-value">{alert.lease_type || 'N/A'}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Start Date</span>
                                    <span className="detail-value">{formatDate(alert.lease_start_date)}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Sq. Footage</span>
                                    <span className="detail-value">{alert.square_footage?.toLocaleString() || 'N/A'} sq ft</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Rent PSF</span>
                                    <span className="detail-value">${alert.base_rent_psf?.toFixed(2) || '0'}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Escalation</span>
                                    <span className="detail-value">{alert.annual_escalation_pct?.toFixed(1) || '0'}%</span>
                                  </div>
                                </div>

                                <div className="expanded-section">
                                  <h4><FiUser size={16} /> Parties</h4>
                                  <div className="detail-row">
                                    <span className="detail-label">Tenant</span>
                                    <span className="detail-value">{alert.tenant_name}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Landlord</span>
                                    <span className="detail-value">{alert.landlord_name || 'N/A'}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Sector</span>
                                    <span className="detail-value">{alert.industry_sector || 'N/A'}</span>
                                  </div>
                                </div>

                                <div className="expanded-section">
                                  <h4><FiCalendar size={16} /> Renewal & Notices</h4>
                                  <div className="detail-row">
                                    <span className="detail-label">Renewal Options</span>
                                    <span className="detail-value">{alert.renewal_options || 'None specified'}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Notice Period</span>
                                    <span className="detail-value">
                                      {alert.renewal_notice_days ? `${alert.renewal_notice_days} days` : 'Not specified'}
                                    </span>
                                  </div>
                                  {alert.notice_deadline_passed && (
                                    <div className="notice-alert-banner">
                                      <FiAlertCircle size={16} />
                                      <span>Renewal notice deadline may have passed! Only {alert.days_to_expiry} days remain but {alert.renewal_notice_days}-day notice is required.</span>
                                    </div>
                                  )}
                                </div>

                                <div className="expanded-section">
                                  <h4><FiMapPin size={16} /> Risk Assessment</h4>
                                  <div className="detail-row">
                                    <span className="detail-label">Risk Score</span>
                                    <span className="detail-value" style={{ color: alert.risk_score > 70 ? '#EF4444' : alert.risk_score > 40 ? '#F59E0B' : '#10B981' }}>
                                      {alert.risk_score.toFixed(1)}
                                    </span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Risk Status</span>
                                    <span className="detail-value">{alert.risk_status}</span>
                                  </div>
                                  <div className="detail-row">
                                    <span className="detail-label">Risk Model</span>
                                    <span className="detail-value">{alert.risk_model}</span>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </AnimatePresence>
            </tbody>
          </table>

          {filteredAlerts.length === 0 && (
            <div className="no-alerts">
              <FiClock size={48} color="rgba(255,255,255,0.3)" />
              <p>No alerts for this filter</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default CriticalDateAlerts;
