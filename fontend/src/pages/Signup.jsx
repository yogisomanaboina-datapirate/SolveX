import React, { useState } from 'react';
import { Heart, Lock, Mail, User, Eye, EyeOff, ArrowRight, ShieldCheck, Siren, Activity, AlertCircle } from 'lucide-react';
import { AuthService } from '../api/services';

export const Signup = ({ onSignupSuccess, onSwitchToLogin }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Form Validations
    if (!name.trim()) {
      setError('Please enter your full name.');
      return;
    }
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
      setError('Please create a password.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match. Please verify your confirm password.');
      return;
    }

    try {
      setLoading(true);
      const res = await AuthService.signup(email.trim(), password, name.trim());
      if (res && res.success) {
        const userData = res.data?.user || { email, name: name.trim() };
        onSignupSuccess(userData);
      } else {
        throw new Error(res?.error?.message || 'Registration failed.');
      }
    } catch (err) {
      console.error("Signup failed:", {
        message: err.message,
        status: err.status,
        data: err.data
      });
      setError(err.message || 'Error creating account. Please try again.');
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
                Emergency Care Portal
              </div>
            </div>
          </div>

          <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-slate-900)', lineHeight: 1.25, marginBottom: '16px' }}>
            Join the autonomous <span style={{ color: 'var(--teal-600)' }}>health revolution.</span>
          </h1>

          <p style={{ fontSize: '1rem', color: 'var(--color-slate-600)', lineHeight: 1.6, marginBottom: '28px' }}>
            Create an account to manage emergency response profiles, active prescriptions, medical report trends, and insurance claims.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.9rem', color: 'var(--color-slate-700)', fontWeight: 500 }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#f0fdf4', color: 'var(--teal-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Activity className="w-4 h-4" />
              </div>
              <span>Personalized Medication Intake & Conflict Scheduling</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.9rem', color: 'var(--color-slate-700)', fontWeight: 500 }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#f0f9ff', color: 'var(--primary-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Siren className="w-4 h-4" />
              </div>
              <span>Immediate GPS Ambulance Triage & Dispatch Access</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.9rem', color: 'var(--color-slate-700)', fontWeight: 500 }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#f0fdf4', color: 'var(--teal-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldCheck className="w-4 h-4" />
              </div>
              <span>Secure Cloud Health Records & Policy Coverage Verification</span>
            </div>
          </div>
        </div>

        {/* Right Column: Sign Up Card */}
        <div className="card" style={{ padding: '36px', boxShadow: 'var(--shadow-lg)', margin: 0 }}>
          <div style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-slate-900)', marginBottom: '6px' }}>
              Create Account
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--color-slate-500)' }}>
              Get started with your personalized LifeLink AI portal
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
              <label className="form-label" htmlFor="signup-name">Full Name</label>
              <div style={{ position: 'relative' }}>
                <input
                  id="signup-name"
                  type="text"
                  className="form-input"
                  style={{ paddingLeft: '38px' }}
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={loading}
                  required
                />
                <User className="w-4 h-4" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-slate-400)' }} />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="signup-email">Email Address</label>
              <div style={{ position: 'relative' }}>
                <input
                  id="signup-email"
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

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label" htmlFor="signup-password">Password</label>
                <div style={{ position: 'relative' }}>
                  <input
                    id="signup-password"
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
                    style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--color-slate-400)', cursor: 'cursor' }}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="signup-confirm-password">Confirm Password</label>
                <div style={{ position: 'relative' }}>
                  <input
                    id="signup-confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    className="form-input"
                    style={{ paddingLeft: '38px', paddingRight: '38px' }}
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                    required
                  />
                  <Lock className="w-4 h-4" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-slate-400)' }} />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--color-slate-400)', cursor: 'cursor' }}
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', padding: '12px', fontSize: '0.95rem', marginTop: '8px', marginBottom: '20px', backgroundColor: 'var(--teal-600)' }}
              disabled={loading}
            >
              <span>{loading ? 'Creating Account...' : 'Sign Up'}</span>
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div style={{ textAlign: 'center', fontSize: '0.88rem', color: 'var(--color-slate-600)' }}>
            Already have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              style={{ background: 'none', border: 'none', color: 'var(--primary-600)', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
            >
              Log In
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
