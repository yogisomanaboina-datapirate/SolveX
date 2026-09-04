import React from 'react';
import { AlertCircle, CheckCircle2, Info, Loader2, AlertTriangle } from 'lucide-react';

export const Badge = ({ type = 'neutral', children }) => {
  const badgeClass = `badge badge-${type.toLowerCase()}`;
  return <span className={badgeClass}>{children}</span>;
};

export const Alert = ({ type = 'info', title, message, children }) => {
  const bgStyles = {
    info: 'bg-sky-50 border-sky-200 text-sky-900',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    warning: 'bg-amber-50 border-amber-200 text-amber-900',
    danger: 'bg-red-50 border-red-200 text-red-900'
  };

  const icons = {
    info: <Info className="w-5 h-5 text-sky-600 flex-shrink-0" />,
    success: <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />,
    warning: <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />,
    danger: <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
  };

  return (
    <div style={{
      padding: '14px 18px',
      borderRadius: '8px',
      border: '1px solid var(--border-color)',
      marginBottom: '16px',
      display: 'flex',
      gap: '12px',
      alignItems: 'flex-start',
      backgroundColor: type === 'danger' ? '#fef2f2' : type === 'warning' ? '#fffbeb' : type === 'success' ? '#f0fdf4' : '#f0f9ff',
      borderColor: type === 'danger' ? '#fecaca' : type === 'warning' ? '#fde68a' : type === 'success' ? '#bbf7d0' : '#bae6fd'
    }}>
      {icons[type]}
      <div style={{ flex: 1 }}>
        {title && <div style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '2px' }}>{title}</div>}
        {message && <div style={{ fontSize: '0.88rem', opacity: 0.9 }}>{message}</div>}
        {children}
      </div>
    </div>
  );
};

export const LoadingSpinner = ({ label = 'Processing...' }) => (
  <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--color-slate-600)' }}>
    <Loader2 className="animate-spin" style={{ width: '32px', height: '32px', margin: '0 auto 12px auto', color: 'var(--primary-600)' }} />
    <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{label}</div>
  </div>
);

export const EmptyState = ({ icon: Icon, title, description, action }) => (
  <div style={{
    padding: '48px 24px',
    textAlign: 'center',
    backgroundColor: 'var(--bg-surface)',
    border: '1px dashed var(--border-color)',
    borderRadius: 'var(--radius-md)',
    margin: '16px 0'
  }}>
    {Icon && <Icon style={{ width: '40px', height: '40px', color: 'var(--color-slate-400)', margin: '0 auto 12px auto' }} />}
    <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-slate-800)', marginBottom: '4px' }}>{title}</h4>
    {description && <p style={{ fontSize: '0.85rem', color: 'var(--color-slate-500)', maxWidth: '400px', margin: '0 auto 16px auto' }}>{description}</p>}
    {action}
  </div>
);
