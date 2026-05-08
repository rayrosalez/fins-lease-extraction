import React, { useState, useEffect, useRef } from 'react';
import { FiBell, FiAlertTriangle, FiClock, FiDollarSign, FiChevronRight } from 'react-icons/fi';
import './NotificationBell.css';

const API_BASE_URL = '/api';

const TIER_COLORS = {
  EXPIRED: '#6B7280',
  CRITICAL: '#EF4444',
  URGENT: '#F59E0B',
  UPCOMING: '#3B82F6',
};

const formatCurrency = (value) => {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
};

const NotificationBell = ({ onNavigate }) => {
  const [data, setData] = useState(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const ref = useRef(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/alerts/critical-dates`);
      if (res.ok) setData(await res.json());
    } catch { /* silent */ }
    setLoading(false);
  };

  const summary = data?.summary || {};
  const criticalCount = (summary.CRITICAL || 0) + (summary.EXPIRED || 0);
  const urgentCount = summary.URGENT || 0;
  const badgeCount = criticalCount + urgentCount;
  const topAlerts = (data?.alerts || []).slice(0, 8);

  return (
    <div className="notif-bell-wrap" ref={ref}>
      <button
        className="notif-bell-btn"
        onClick={() => setOpen(!open)}
        title="Notifications"
      >
        <FiBell size={20} />
        {badgeCount > 0 && (
          <span className="notif-badge">{badgeCount > 99 ? '99+' : badgeCount}</span>
        )}
      </button>

      {open && (
        <div className="notif-dropdown">
          <div className="notif-header">
            <span className="notif-header-title">Lease Alerts</span>
            {data && (
              <span className="notif-header-count">{data.total_alerts} total</span>
            )}
          </div>

          {/* Summary strip */}
          {data && (
            <div className="notif-summary">
              {criticalCount > 0 && (
                <div className="notif-summary-pill" style={{ '--pill-color': TIER_COLORS.CRITICAL }}>
                  <FiAlertTriangle size={12} />
                  <span>{criticalCount} critical</span>
                </div>
              )}
              {urgentCount > 0 && (
                <div className="notif-summary-pill" style={{ '--pill-color': TIER_COLORS.URGENT }}>
                  <FiClock size={12} />
                  <span>{urgentCount} urgent</span>
                </div>
              )}
              {(summary.UPCOMING || 0) > 0 && (
                <div className="notif-summary-pill" style={{ '--pill-color': TIER_COLORS.UPCOMING }}>
                  <FiClock size={12} />
                  <span>{summary.UPCOMING} upcoming</span>
                </div>
              )}
              {data.total_revenue_at_risk > 0 && (
                <div className="notif-summary-pill notif-revenue-pill">
                  <FiDollarSign size={12} />
                  <span>{formatCurrency(data.total_revenue_at_risk)} at risk</span>
                </div>
              )}
            </div>
          )}

          {/* Alert list */}
          <div className="notif-list">
            {loading && (
              <div className="notif-empty">Loading...</div>
            )}
            {!loading && topAlerts.length === 0 && (
              <div className="notif-empty">No upcoming lease alerts</div>
            )}
            {topAlerts.map((alert) => (
              <div
                key={alert.lease_id}
                className="notif-item"
                onClick={() => {
                  setOpen(false);
                  if (onNavigate) onNavigate('portfolio');
                }}
              >
                <div
                  className="notif-item-indicator"
                  style={{ background: TIER_COLORS[alert.alert_tier] || '#6B7280' }}
                />
                <div className="notif-item-body">
                  <div className="notif-item-top">
                    <span className="notif-item-tenant">{alert.tenant_name}</span>
                    <span
                      className="notif-item-days"
                      style={{ color: TIER_COLORS[alert.alert_tier] || '#6B7280' }}
                    >
                      {alert.days_to_expiry < 0
                        ? `${Math.abs(alert.days_to_expiry)}d overdue`
                        : `${alert.days_to_expiry}d`}
                    </span>
                  </div>
                  <div className="notif-item-bottom">
                    <span className="notif-item-detail">
                      {alert.industry_sector || 'N/A'} &middot; {formatCurrency(alert.estimated_annual_rent)}/yr
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          {topAlerts.length > 0 && (
            <button
              className="notif-footer"
              onClick={() => {
                setOpen(false);
                if (onNavigate) onNavigate('portfolio');
              }}
            >
              View all in Portfolio <FiChevronRight size={14} />
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
