import React, { useState, useEffect } from 'react';
import { Siren, Pill, FileText, ShieldCheck, Bed, MessageSquareHeart, ArrowRight, Activity, CheckCircle2, Clock } from 'lucide-react';
import { Badge, Alert, LoadingSpinner, EmptyState } from '../components/CommonUI';
import { MedicationService, InsuranceService, BedService } from '../api/services';

export const Dashboard = ({ setActiveTab }) => {
  const [loading, setLoading] = useState(true);
  const [medications, setMedications] = useState([]);
  const [bedInfo, setBedInfo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [medRes, bedRes] = await Promise.allSettled([
          MedicationService.getMedications('user_123'),
          BedService.getHospitalBeds('HOSP-01')
        ]);

        if (medRes.status === 'fulfilled' && medRes.value?.data) {
          setMedications(medRes.value.data);
        }
        if (bedRes.status === 'fulfilled' && bedRes.value?.data) {
          setBedInfo(bedRes.value.data);
        }
      } catch (err) {
        setError('Connected to Backend gateway in fallback mode.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  return (
    <div>
      {/* Emergency Banner Trigger */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '20px 24px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '10px',
            backgroundColor: 'var(--status-critical-bg)',
            color: 'var(--status-critical)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Siren style={{ width: '24px', height: '24px' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-slate-900)' }}>Emergency Triage & Ambulance Dispatch</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-slate-600)' }}>Autonomous symptom assessment, real hospital selection, and ambulance dispatch.</p>
          </div>
        </div>
        <button className="btn btn-emergency" onClick={() => setActiveTab('emergency')}>
          <span>Assess Emergency</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Grid of 4 Main Care Modules */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        
        {/* Module 1: Medications */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Pill style={{ color: 'var(--primary-600)' }} />
              <span>Today's Medications</span>
            </div>
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={() => setActiveTab('medications')}>
              View Schedule
            </button>
          </div>

          {loading ? (
            <LoadingSpinner label="Loading prescription schedule..." />
          ) : medications.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {medications.map((med, idx) => (
                <div key={idx} style={{
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-surface-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-slate-900)' }}>{med.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-slate-600)' }}>{med.dosage} • Times: {med.schedule?.join(', ')}</div>
                  </div>
                  <Badge type="medium"><Clock className="w-3 h-3" /> Scheduled</Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState 
              icon={Pill} 
              title="No active reminders" 
              description="No prescribed medication schedule loaded yet."
              action={
                <button className="btn btn-outline" style={{ fontSize: '0.8rem' }} onClick={() => setActiveTab('medications')}>
                  Generate Schedule
                </button>
              }
            />
          )}
        </div>

        {/* Module 2: Hospital Bed Availability */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Bed style={{ color: 'var(--teal-600)' }} />
              <span>Hospital Capacity & Beds</span>
            </div>
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={() => setActiveTab('beds')}>
              Optimize Beds
            </button>
          </div>

          {bedInfo ? (
            <div>
              <div style={{ fontSize: '0.85rem', color: 'var(--color-slate-600)', marginBottom: '14px' }}>
                Facility: <strong>{bedInfo.hospitalId || 'Apollo Jubilee Hills'}</strong> (Source of Truth)
              </div>
              <div className="grid-3">
                <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#f0f9ff', textAlign: 'center', border: '1px solid #bae6fd' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--primary-700)' }}>{bedInfo.ICU}</div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-slate-600)' }}>ICU Beds</div>
                </div>
                <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#f0fdf4', textAlign: 'center', border: '1px solid #bbf7d0' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--teal-700)' }}>{bedInfo.ventilator}</div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-slate-600)' }}>Ventilators</div>
                </div>
                <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#f8fafc', textAlign: 'center', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-slate-800)' }}>{bedInfo.general}</div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-slate-600)' }}>General Beds</div>
                </div>
              </div>
            </div>
          ) : (
            <EmptyState icon={Bed} title="Bed data loading" description="Fetching live hospital inventory from Backend..." />
          )}
        </div>

      </div>

      {/* Grid of Secondary Care Tools */}
      <div className="grid-3">
        {/* Tool 1: Medical Reports */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><FileText className="w-5 h-5 text-indigo-600" /> Medical Reports</div>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-slate-600)', marginBottom: '16px' }}>
            Analyze lab results, extract findings, and visualize multi-report parameter trends.
          </p>
          <button className="btn btn-outline" style={{ width: '100%' }} onClick={() => setActiveTab('reports')}>
            Analyze Reports
          </button>
        </div>

        {/* Tool 2: Insurance Claims */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><ShieldCheck className="w-5 h-5 text-emerald-600" /> Insurance & Claims</div>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-slate-600)', marginBottom: '16px' }}>
            Check emergency policy coverage, pre-authorization, and submit automated claim inquiries.
          </p>
          <button className="btn btn-outline" style={{ width: '100%' }} onClick={() => setActiveTab('insurance')}>
            Verify Coverage
          </button>
        </div>

        {/* Tool 3: AI Assistant */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><MessageSquareHeart className="w-5 h-5 text-sky-600" /> AI Health Assistant</div>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-slate-600)', marginBottom: '16px' }}>
            Ask health queries, review user lab history, and receive guided medical answers.
          </p>
          <button className="btn btn-outline" style={{ width: '100%' }} onClick={() => setActiveTab('chat')}>
            Launch Assistant
          </button>
        </div>
      </div>
    </div>
  );
};
