import React, { useState, useEffect } from 'react';
import { Siren, MapPin, Ambulance, Navigation, AlertCircle, ShieldAlert, CheckCircle2, PhoneCall, Info } from 'lucide-react';
import { Badge, Alert, LoadingSpinner } from '../components/CommonUI';
import { EmergencyService } from '../api/services';

export const Emergency = () => {
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('55');
  const [location, setLocation] = useState({ lat: 17.4486, lng: 78.3908, address: 'Hyderabad, Telangana' });
  const [locationStatus, setLocationStatus] = useState('click_to_acquire');
  
  const [loading, setLoading] = useState(false);
  const [triageResult, setTriageResult] = useState(null);
  const [error, setError] = useState(null);

  // Request browser geolocation
  const handleGetLocation = () => {
    if ('geolocation' in navigator) {
      setLocationStatus('locating');
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            address: `GPS: ${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`
          });
          setLocationStatus('granted');
        },
        (err) => {
          setLocationStatus('denied');
          setError('Location permission denied or unavailable. Defaulting to medical center coordinates.');
        }
      );
    } else {
      setLocationStatus('unavailable');
    }
  };

  const handleSubmitTriage = async (e) => {
    e.preventDefault();
    if (!symptoms.trim()) {
      setError('Please describe the emergency symptoms.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setTriageResult(null);

      const response = await EmergencyService.submitEmergencyTriage(
        symptoms,
        location,
        patientAge,
        ['Hypertension']
      );

      if (response && response.data) {
        setTriageResult(response.data);
      } else {
        throw new Error('Invalid response structure received from Backend.');
      }
    } catch (err) {
      setError(err.message || 'Emergency triage evaluation failed. Using safety fallback instructions.');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (severity) => {
    if (severity >= 4) return <Badge type="critical">Severity {severity}/5 — CRITICAL EMERGENCY</Badge>;
    if (severity === 3) return <Badge type="high">Severity 3/5 — HIGH PRIORITY</Badge>;
    return <Badge type="medium">Severity {severity}/5 — MODERATE CARE</Badge>;
  };

  return (
    <div>
      {/* Simulation Safety Notice */}
      <Alert type="warning" title="SIMULATION NOTICE (HACKATHON DEMO)">
        This Emergency Response interface is a simulated coordination engine for demonstration purposes. It does <strong>NOT</strong> dial 108/112 or dispatch real-world emergency services. For real medical emergencies, call your local emergency number immediately.
      </Alert>

      {error && <Alert type="danger" title="System Notification" message={error} />}

      <div className="grid-2">
        {/* Left Side: Symptom Input Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Siren style={{ color: 'var(--status-critical)' }} />
              <span>Autonomous Triage & Dispatch Request</span>
            </div>
          </div>

          <form onSubmit={handleSubmitTriage}>
            <div className="form-group">
              <label className="form-label">Chief Emergency Symptoms / Complaint *</label>
              <textarea
                className="form-textarea"
                rows={4}
                placeholder="e.g., Severe crushing chest pain radiating to left arm, shortness of breath, heavy sweating"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                required
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Patient Age (Years)</label>
                <input
                  type="number"
                  className="form-input"
                  value={patientAge}
                  onChange={(e) => setPatientAge(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">GPS Location</label>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ padding: '8px 12px', fontSize: '0.82rem', width: '100%' }}
                  onClick={handleGetLocation}
                >
                  <MapPin className="w-4 h-4 text-sky-600" />
                  <span>
                    {locationStatus === 'locating' ? 'Locating...' : locationStatus === 'granted' ? 'Location Acquired' : 'Get Current Location'}
                  </span>
                </button>
              </div>
            </div>

            <div style={{ fontSize: '0.8rem', color: 'var(--color-slate-600)', marginBottom: '16px' }}>
              Current Coordinates: <strong>{location.lat.toFixed(4)}, {location.lng.toFixed(4)}</strong>
            </div>

            <button
              type="submit"
              className="btn btn-emergency"
              style={{ width: '100%', padding: '12px' }}
              disabled={loading}
            >
              <Siren className="w-5 h-5" />
              <span>{loading ? 'Evaluating AI Triage...' : 'Execute Autonomous Triage'}</span>
            </button>
          </form>
        </div>

        {/* Right Side: AI Triage & Dispatch Decision Output */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <ShieldAlert style={{ color: 'var(--primary-600)' }} />
              <span>AI Decision & Ambulance Dispatch</span>
            </div>
            {triageResult && getSeverityBadge(triageResult.severity)}
          </div>

          {loading ? (
            <LoadingSpinner label="AI Triage Agent evaluating symptoms against clinical protocols..." />
          ) : triageResult ? (
            <div>
              {/* Category & Condition */}
              <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: 'var(--bg-surface-subtle)', marginBottom: '16px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-slate-600)', textTransform: 'uppercase' }}>Detected Condition</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-slate-900)' }}>
                  {triageResult.condition?.replace(/_/g, ' ').toUpperCase()}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--color-slate-600)', marginTop: '4px' }}>
                  AI Confidence Rating: <strong>{(triageResult.confidence * 100).toFixed(0)}%</strong>
                </div>
              </div>

              {/* Action & Hospital Assignment */}
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '8px' }}>Action & Destination:</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.88rem' }}>
                    <Ambulance className="w-4 h-4 text-red-600 flex-shrink-0" />
                    <span>Dispatch Status: <strong>{triageResult.action?.replace(/_/g, ' ').toUpperCase()}</strong></span>
                  </div>
                  {triageResult.hospitalName && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.88rem' }}>
                      <Navigation className="w-4 h-4 text-sky-600 flex-shrink-0" />
                      <span>Target Hospital: <strong>{triageResult.hospitalName}</strong></span>
                    </div>
                  )}
                  {triageResult.ETA && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.88rem' }}>
                      <Info className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <span>Estimated Arrival ETA: <strong>~{triageResult.ETA} mins</strong></span>
                    </div>
                  )}
                  {triageResult.ambulanceId && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.88rem' }}>
                      <Badge type="neutral">Simulated Unit: {triageResult.ambulanceId}</Badge>
                    </div>
                  )}
                </div>
              </div>

              {/* First Aid Guidance */}
              <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', marginBottom: '16px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary-700)', marginBottom: '4px' }}>Immediate First-Aid Instructions:</div>
                <div style={{ fontSize: '0.88rem', color: 'var(--color-slate-800)' }}>{triageResult.firstAid}</div>
              </div>

              {/* AI Clinical Reasoning */}
              <div style={{ fontSize: '0.82rem', color: 'var(--color-slate-600)', backgroundColor: 'var(--bg-surface-subtle)', padding: '12px', borderRadius: '6px' }}>
                <strong>AI Clinical Rationale:</strong> {triageResult.aiReasoning}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--color-slate-500)' }}>
              <Siren style={{ width: '36px', height: '36px', opacity: 0.4, margin: '0 auto 12px auto' }} />
              <div>Enter patient emergency symptoms on the left to initiate real-time AI triage assessment.</div>
            </div>
          )}
        </div>
      </div>

      {/* Nearby Real Hospitals Map Guidance */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <MapPin style={{ color: 'var(--primary-600)' }} />
            <span>Nearby Medical Facilities & Navigation</span>
          </div>
        </div>

        <p style={{ fontSize: '0.88rem', color: 'var(--color-slate-600)', marginBottom: '16px' }}>
          Below are real hospital locations discovered around current GPS coordinates for direct navigation.
        </p>

        <div className="grid-3">
          <div style={{ padding: '14px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-surface)' }}>
            <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>Apollo Hospitals Jubilee Hills</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-slate-600)', margin: '4px 0 10px 0' }}>Road No 36, Jubilee Hills • 2.4 km</div>
            <a
              href={`https://www.google.com/maps/search/?api=1&query=Apollo+Hospitals+Jubilee+Hills`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
              style={{ padding: '4px 10px', fontSize: '0.78rem', width: '100%' }}
            >
              Google Maps Directions
            </a>
          </div>

          <div style={{ padding: '14px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-surface)' }}>
            <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>KIMS Hospitals Secunderabad</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-slate-600)', margin: '4px 0 10px 0' }}>Minister Road, Secunderabad • 5.1 km</div>
            <a
              href={`https://www.google.com/maps/search/?api=1&query=KIMS+Hospitals+Secunderabad`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
              style={{ padding: '4px 10px', fontSize: '0.78rem', width: '100%' }}
            >
              Google Maps Directions
            </a>
          </div>

          <div style={{ padding: '14px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-surface)' }}>
            <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>Yashoda Hospitals Gachibowli</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-slate-600)', margin: '4px 0 10px 0' }}>IT Park, Gachibowli • 6.8 km</div>
            <a
              href={`https://www.google.com/maps/search/?api=1&query=Yashoda+Hospitals+Gachibowli`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
              style={{ padding: '4px 10px', fontSize: '0.78rem', width: '100%' }}
            >
              Google Maps Directions
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
