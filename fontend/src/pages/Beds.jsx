import React, { useState, useEffect } from 'react';
import { Bed, Activity, CheckCircle2, AlertTriangle, Building, Zap } from 'lucide-react';
import { Badge, Alert, LoadingSpinner } from '../components/CommonUI';
import { BedService } from '../api/services';

export const Beds = () => {
  const [hospitalId, setHospitalId] = useState('HOSP-01');
  const [bedType, setBedType] = useState('ICU');
  const [urgency, setUrgency] = useState('CRITICAL');
  const [specialty, setSpecialty] = useState('CARDIOLOGY');

  const [inventory, setInventory] = useState(null);
  const [loadingInventory, setLoadingInventory] = useState(false);

  const [optimizing, setOptimizing] = useState(false);
  const [optResult, setOptResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchInventory() {
      try {
        setLoadingInventory(true);
        const res = await BedService.getHospitalBeds(hospitalId);
        if (res && res.data) {
          setInventory(res.data);
        }
      } catch (err) {
        setError('Failed to fetch live bed inventory from Backend.');
      } finally {
        setLoadingInventory(false);
      }
    }
    fetchInventory();
  }, [hospitalId]);

  const handleOptimize = async (e) => {
    e.preventDefault();
    try {
      setOptimizing(true);
      setError(null);
      setOptResult(null);

      const res = await BedService.optimizeBeds(hospitalId, bedType, urgency, specialty);
      if (res && res.data) {
        setOptResult(res.data);
      } else {
        throw new Error('Invalid optimization response received from Backend.');
      }
    } catch (err) {
      setError(err.message || 'Bed optimization failed.');
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div>
      {error && <Alert type="danger" title="Inventory Notice" message={error} />}

      <div className="grid-2" style={{ marginBottom: '24px' }}>
        {/* Backend Inventory Source of Truth */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Building style={{ color: 'var(--teal-600)' }} />
              <span>Live Inventory (Backend Source of Truth)</span>
            </div>
            <Badge type="neutral">Hospital: {hospitalId}</Badge>
          </div>

          {loadingInventory ? (
            <LoadingSpinner label="Fetching bed inventory..." />
          ) : inventory ? (
            <div className="grid-3">
              <div style={{ padding: '16px', borderRadius: '8px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary-700)' }}>{inventory.ICU}</div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-slate-700)' }}>Available ICU Beds</div>
              </div>
              <div style={{ padding: '16px', borderRadius: '8px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--teal-700)' }}>{inventory.ventilator}</div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-slate-700)' }}>Ventilators</div>
              </div>
              <div style={{ padding: '16px', borderRadius: '8px', backgroundColor: '#f8fafc', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--color-slate-800)' }}>{inventory.general}</div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-slate-700)' }}>General Ward Beds</div>
              </div>
            </div>
          ) : (
            <div>No inventory record loaded.</div>
          )}
        </div>

        {/* AI Bed Optimization Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Zap style={{ color: 'var(--primary-600)' }} />
              <span>AI Bed Optimization & Capacity Engine</span>
            </div>
          </div>

          <form onSubmit={handleOptimize}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Required Bed Category</label>
                <select className="form-select" value={bedType} onChange={(e) => setBedType(e.target.value)}>
                  <option value="ICU">ICU (Intensive Care)</option>
                  <option value="VENTILATOR">Ventilator Unit</option>
                  <option value="GENERAL">General Ward</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Patient Urgency</label>
                <select className="form-select" value={urgency} onChange={(e) => setUrgency(e.target.value)}>
                  <option value="CRITICAL">CRITICAL (Immediate)</option>
                  <option value="HIGH">HIGH (Urgent)</option>
                  <option value="MEDIUM">MEDIUM (Standard)</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Required Specialty Department</label>
              <select className="form-select" value={specialty} onChange={(e) => setSpecialty(e.target.value)}>
                <option value="CARDIOLOGY">CARDIOLOGY</option>
                <option value="PULMONOLOGY">PULMONOLOGY</option>
                <option value="NEUROLOGY">NEUROLOGY</option>
                <option value="TRAUMA_CARE">TRAUMA CARE</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '10px' }} disabled={optimizing}>
              <Bed className="w-4 h-4" />
              <span>{optimizing ? 'Calculating Capacity...' : 'Run Bed Optimization'}</span>
            </button>
          </form>
        </div>
      </div>

      {/* Optimization Recommendation Result */}
      {optResult && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <span>Optimal Hospital Bed Allocation Recommendation</span>
            </div>
            <Badge type="high">AI Confidence: {(optResult.confidence * 100).toFixed(0)}%</Badge>
          </div>

          <div className="grid-2" style={{ marginBottom: '16px' }}>
            <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-700)' }}>RECOMMENDED HOSPITAL</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-slate-900)', marginTop: '4px' }}>
                {optResult.recommendedHospitalName}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--color-slate-600)', marginTop: '4px' }}>
                Allocated Unit: <strong>{optResult.allocatedBedType}</strong> • Beds Available: <strong>{optResult.bedsAvailable}</strong>
              </div>
            </div>

            <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: 'var(--bg-surface-subtle)' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-slate-700)', marginBottom: '4px' }}>AI ALLOCATION REASONING</div>
              <div style={{ fontSize: '0.88rem', color: 'var(--color-slate-800)' }}>{optResult.aiReasoning}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
