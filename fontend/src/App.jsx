import React, { useState, useEffect } from 'react';
import { Navigation, Header } from './components/Navigation';
import { Dashboard } from './pages/Dashboard';
import { Emergency } from './pages/Emergency';
import { Insurance } from './pages/Insurance';
import { Beds } from './pages/Beds';
import { Medications } from './pages/Medications';
import { Reports } from './pages/Reports';
import { Chatbot } from './pages/Chatbot';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("React Component Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', backgroundColor: '#fef2f2', color: '#991b1b', fontFamily: 'sans-serif', minHeight: '100vh' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px' }}>LifeLink AI Render Error</h2>
          <p style={{ fontSize: '0.9rem', marginBottom: '12px' }}>An error occurred while rendering the dashboard. Details below:</p>
          <pre style={{ fontSize: '0.85rem', backgroundColor: '#fee2e2', padding: '12px', borderRadius: '6px', overflowX: 'auto' }}>
            {this.state.error?.toString()}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{ marginTop: '16px', padding: '8px 16px', backgroundColor: '#dc2626', color: '#ffffff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
          >
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState({ name: 'Demo Patient', id: 'user_123' });
  
  // Auth state: 'authenticated' | 'login' | 'signup'
  const [authMode, setAuthMode] = useState(() => {
    const path = window.location.pathname;
    if (path === '/signup') return 'signup';
    if (path === '/login') return 'login';
    const token = localStorage.getItem('auth_token');
    return token ? 'authenticated' : 'login';
  });

  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/signup') setAuthMode('signup');
      else if (path === '/login') setAuthMode('login');
      else setAuthMode(localStorage.getItem('auth_token') ? 'authenticated' : 'login');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleLoginSuccess = (userData) => {
    if (userData && userData.name) {
      setUser({ name: userData.name, id: userData.uid || 'user_123' });
    }
    setAuthMode('authenticated');
    window.history.pushState({}, '', '/');
  };

  const handleSignupSuccess = (userData) => {
    if (userData && userData.name) {
      setUser({ name: userData.name, id: userData.uid || 'user_123' });
    }
    setAuthMode('authenticated');
    window.history.pushState({}, '', '/');
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setAuthMode('login');
    window.history.pushState({}, '', '/login');
  };

  const pageTitles = {
    dashboard: 'Health Coordination Dashboard',
    emergency: 'Emergency Response & Autonomous Triage',
    medications: 'Medication Schedule & Conflict Engine',
    reports: 'Medical Reports & Parameter Trend Analyzer',
    insurance: 'Insurance Claims & Policy Verification',
    beds: 'Hospital Bed Inventory & Capacity Optimization',
    chat: 'LifeLink AI Conversational Health Assistant'
  };

  if (authMode === 'login') {
    return (
      <ErrorBoundary>
        <Login
          onLoginSuccess={handleLoginSuccess}
          onSwitchToSignup={() => {
            setAuthMode('signup');
            window.history.pushState({}, '', '/signup');
          }}
        />
      </ErrorBoundary>
    );
  }

  if (authMode === 'signup') {
    return (
      <ErrorBoundary>
        <Signup
          onSignupSuccess={handleSignupSuccess}
          onSwitchToLogin={() => {
            setAuthMode('login');
            window.history.pushState({}, '', '/login');
          }}
        />
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <div className="app-container">
        {/* Sidebar Shell */}
        <Navigation activeTab={activeTab} setActiveTab={setActiveTab} user={user} />

        {/* Main Content Area */}
        <div className="main-content">
          <Header 
            title={pageTitles[activeTab] || 'LifeLink AI'} 
            activeTab={activeTab} 
            setActiveTab={setActiveTab} 
            user={user}
            onLogout={handleLogout}
          />

          <main className="page-body">
            {activeTab === 'dashboard' && <Dashboard setActiveTab={setActiveTab} />}
            {activeTab === 'emergency' && <Emergency />}
            {activeTab === 'medications' && <Medications />}
            {activeTab === 'reports' && <Reports />}
            {activeTab === 'insurance' && <Insurance />}
            {activeTab === 'beds' && <Beds />}
            {activeTab === 'chat' && <Chatbot setActiveTab={setActiveTab} />}
          </main>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
