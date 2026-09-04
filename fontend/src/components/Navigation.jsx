import React from 'react';
import { 
  Activity, 
  Siren, 
  Pill, 
  FileText, 
  ShieldCheck, 
  Bed, 
  MessageSquareHeart, 
  User,
  Heart,
  LogOut,
  Wifi
} from 'lucide-react';

export const Navigation = ({ activeTab, setActiveTab, user = { name: 'Demo Patient', id: 'user_123' } }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'emergency', label: 'Emergency Response', icon: Siren, isEmergency: true },
    { id: 'medications', label: 'Medications & Reminders', icon: Pill },
    { id: 'reports', label: 'Medical Reports', icon: FileText },
    { id: 'insurance', label: 'Insurance & Claims', icon: ShieldCheck },
    { id: 'beds', label: 'Hospital Beds & Surge', icon: Bed },
    { id: 'chat', label: 'AI Health Assistant', icon: MessageSquareHeart },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">
          <Heart className="w-5 h-5 fill-current" />
        </div>
        <div>
          <div className="brand-title">LifeLink AI</div>
          <div className="brand-subtitle">Emergency Care Portal</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const classNames = `nav-item ${item.isEmergency ? 'nav-item-emergency' : ''} ${isActive ? 'active' : ''}`;
          
          return (
            <button
              key={item.id}
              className={classNames}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ padding: '16px', borderTop: '1px solid var(--color-slate-800)', fontSize: '0.8rem', color: 'var(--color-slate-400)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <Wifi style={{ width: '14px', height: '14px', color: '#22c55e' }} />
          <span>Backend Connected (Port 8001)</span>
        </div>
        <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>System status: Online & Ready</div>
      </div>
    </aside>
  );
};

export const Header = ({ title, activeTab, setActiveTab, user = { name: 'Demo Patient' }, onLogout }) => (
  <header className="header">
    <div className="header-title">{title}</div>
    <div className="header-actions">
      <button 
        className="btn btn-emergency" 
        style={{ padding: '6px 14px', fontSize: '0.82rem' }}
        onClick={() => setActiveTab('emergency')}
      >
        <Siren className="w-4 h-4" />
        <span>Emergency Assist</span>
      </button>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem', fontWeight: 600, color: 'var(--color-slate-700)' }}>
        <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--color-slate-200)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-slate-700)' }}>
          <User className="w-4 h-4" />
        </div>
        <span>{user.name}</span>
      </div>

      {onLogout && (
        <button
          type="button"
          className="btn btn-secondary"
          style={{ padding: '6px 10px', fontSize: '0.8rem' }}
          onClick={onLogout}
          title="Sign Out"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      )}
    </div>
  </header>
);
