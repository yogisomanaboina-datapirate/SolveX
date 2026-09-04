import React, { useState } from 'react';
import { Heart, Lock, Mail, Eye, EyeOff, ArrowRight, ShieldCheck, Siren, Activity, AlertCircle } from 'lucide-react';
import { AuthService } from '../api/services';

export const Login = ({ onLoginSuccess, onSwitchToSignup }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!email.trim()) {
      setError('Please enter your email address.');
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }

    try {
      setLoading(true);
      const res = await AuthService.login(email.trim(), password);
      if (res && res.success) {
        const userData = res.data?.user || { email, name: email.split('@')[0] };
        onLoginSuccess(userData);
      } else {
        throw new Error(res?.error?.message || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      console.error("Login failed:", {
        message: err.message,
        status: err.status,
        data: err.data
      });
      setError(err.message || 'Authentication error. Please verify your email and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--bg-app)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1000px',
        width: '100%',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '40px',
        alignItems: 'center'
      }}>
        {/* Left Column: LifeLink AI Branding */}
        <div style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div className="brand-icon" style={{ width: '48px', height: '48px', borderRadius: '12px' }}>
              <Heart className="w-6 h-6 fill-current" />
            </div>
            <div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--color-slate-900)', letterSpacing: '-0.03em' }}>
                LifeLink AI
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-slate-500)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>
                Emergency & Health Care Portal
              </div>
            </div>
          </div>

          <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-slate-900)', lineHeight: 1.25, marginBottom: '16px' }}>
            Healthcare coordination, <span style={{ color: 'var(--primary-600)' }}>simplified.</span>
          </h1>

          <p style={{ fontSize: '1rem', color: 'var(--color-slate-600)', lineHeight: 1.6, marginBottom: '28px' }}>
            Autonomous emergency response, AI-driven symptom triage, medication conflict detection, and lab report trend analysis — all in one platform.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.9rem', color: 'var(--color-slate-700)', fontWeight: 500 }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#f0f9ff', color: 'var(--primary-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Siren className="w-4 h-4" />
              </div>
              <span>Real-Time Autonomous Emergency Ambulance Dispatch</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.9rem', color: 'var(--color-slate-700)', fontWeight: 500 }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#f0fdf4', color: 'var(--teal-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Activity className="w-4 h-4" />
              </div>
              <span>Intelligent Medication Conflict & Reminder Engine</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.9rem', color: 'var(--color-slate-700)', fontWeight: 500 }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#f0f9ff', color: 'var(--primary-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldCheck className="w-4 h-4" />
              </div>
              <span>Instant Insurance Policy Verification & Claim Analysis</span>
            </div>
          </div>
        </div>

        {/* Right Column: Login Card */}
        <div className="card" style={{ padding: '36px', boxShadow: 'var(--shadow-lg)', margin: 0 }}>
          <div style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-slate-900)', marginBottom: '6px' }}>
              Welcome Back
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--color-slate-500)' }}>
              Sign in to access your LifeLink AI health portal
            </p>
          </div>

          {error && (
            <div style={{
              backgroundColor: 'var(--status-critical-bg)',
              border: '1px solid rgba(220,38,38,0.2)',
              borderRadius: '8px',
              padding: '12px 14px',
              marginBottom: '20px',
              color: 'var(--status-critical)',
              fontSize: '0.88rem',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="login-email">Email Address</label>
              <div style={{ position: 'relative' }}>
                <input
                  id="login-email"
                  type="email"
                  className="form-input"
                  style={{ paddingLeft: '38px' }}
                  placeholder="patient@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  required
                />
                <Mail className="w-4 h-4" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-slate-400)' }} />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label className="form-label" htmlFor="login-password" style={{ marginBottom: 0 }}>Password</label>
              </div>
              <div style={{ position: 'relative' }}>
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  style={{ paddingLeft: '38px', paddingRight: '38px' }}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  required
                />
                <Lock className="w-4 h-4" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-slate-400)' }} />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--color-slate-400)', cursor: 'pointer' }}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', padding: '12px', fontSize: '0.95rem', marginBottom: '20px' }}
              disabled={loading}
            >
              <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div style={{ textAlign: 'center', fontSize: '0.88rem', color: 'var(--color-slate-600)' }}>
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToSignup}
              style={{ background: 'none', border: 'none', color: 'var(--primary-600)', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
            >
              Sign Up
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
