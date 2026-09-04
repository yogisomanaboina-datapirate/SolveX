import React, { useState } from 'react';
import { ShieldCheck, FileCheck, DollarSign, Building, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Badge, Alert, LoadingSpinner } from '../components/CommonUI';
import { InsuranceService } from '../api/services';

export const Insurance = () => {
  const [patientId, setPatientId] = useState('user_123');
  const [provider, setProvider] = useState('Apollo Health Insurance');
  const [policyNumber, setPolicyNumber] = useState('POL-99281');
  const [claimedAmount, setClaimedAmount] = useState('15000');
  
  const [loading, setLoading] = useState(false);
  const [claimData, setClaimData] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmitClaim = async (e) => {
    e.preventDefault();
    if (!policyNumber || !claimedAmount) {
      setError('Please provide valid policy number and claim amount.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setClaimData(null);

      const response = await InsuranceService.submitClaim(
        patientId,
        provider,
        policyNumber,
        claimedAmount
      );

      if (response && response.data) {
        setClaimData(response.data);
      } else {
        throw new Error('Invalid insurance claim response received from Backend.');
      }
    } catch (err) {
      setError(err.message || 'Insurance claim analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {error && <Alert type="danger" title="Insurance Inquiry Notice" message={error} />}

      <div className="grid-2">
        {/* Claim Inquiry Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <ShieldCheck style={{ color: 'var(--teal-600)' }} />
              <span>Submit Insurance Inquiry & Claim</span>
            </div>
          </div>

          <form onSubmit={handleSubmitClaim}>
            <div className="form-group">
              <label className="form-label">Insurance Provider</label>
              <select className="form-select" value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="Apollo Health Insurance">Apollo Health Insurance</option>
                <option value="Star Health Insurance">Star Health Insurance</option>
                <option value="Max Bupa Health">Max Bupa Health</option>
                <option value="HDFC ERGO">HDFC ERGO Health</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Policy Number *</label>
              <input
                type="text"
                className="form-input"
                value={policyNumber}
                onChange={(e) => setPolicyNumber(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Requested Claim Amount (INR) *</label>
              <input
                type="number"
                className="form-input"
                value={claimedAmount}
                onChange={(e) => setClaimedAmount(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px' }} disabled={loading}>
              <FileCheck className="w-5 h-5" />
              <span>{loading ? 'Analyzing Policy & Claims...' : 'Submit Claim Analysis'}</span>
            </button>
          </form>
        </div>

        {/* Claim Decision & Policy Verification */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Building style={{ color: 'var(--primary-600)' }} />
              <span>Verified Claim Analysis Result</span>
            </div>
            {claimData && <Badge type="low">{claimData.status}</Badge>}
          </div>

          {loading ? (
            <LoadingSpinner label="AI Claims Agent calculating coverage and verifying policy records..." />
          ) : claimData ? (
            <div>
              <div style={{ padding: '16px', borderRadius: '8px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', marginBottom: '16px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--teal-700)', textTransform: 'uppercase' }}>Approved Reimbursement Estimate</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--teal-700)', margin: '4px 0' }}>
                  ₹{claimData.approvedAmount?.toLocaleString('en-IN')} INR
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--color-slate-600)' }}>
                  Claim Reference ID: <strong>{claimData.claimId}</strong>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px', fontSize: '0.88rem' }}>
                <div>Policy Number: <strong>{claimData.policyNumber}</strong></div>
                <div>Insurance Provider: <strong>{claimData.insuranceProvider}</strong></div>
                <div>Verification Timestamp: <strong>{new Date(claimData.timestamp).toLocaleString()}</strong></div>
              </div>

              <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: 'var(--bg-surface-subtle)', fontSize: '0.85rem' }}>
                <strong style={{ color: 'var(--color-slate-900)' }}>AI Policy Analysis & Guidance:</strong>
                <p style={{ marginTop: '4px', color: 'var(--color-slate-700)' }}>{claimData.aiReasoning}</p>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--color-slate-500)' }}>
              <ShieldCheck style={{ width: '36px', height: '36px', opacity: 0.4, margin: '0 auto 12px auto' }} />
              <div>Enter policy details on the left to verify emergency insurance coverage and file claims.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
