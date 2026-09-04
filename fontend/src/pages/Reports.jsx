import React, { useState } from 'react';
import { FileText, TrendingUp, BarChart2, Plus, AlertCircle, CheckCircle2, Info } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Badge, Alert, LoadingSpinner } from '../components/CommonUI';
import { ReportService } from '../api/services';

export const Reports = () => {
  const [reportTitle, setReportTitle] = useState('CBC Lab Report');
  const [reportDate, setReportDate] = useState('2026-08-10');
  const [reportText, setReportText] = useState('CBC Report: Hemoglobin 14.2 g/dL, WBC 6,500 /mcL, Platelets 220,000 /mcL, Fasting Blood Sugar 95 mg/dL.');
  
  const [includeHistorical, setIncludeHistorical] = useState(true);
  const [prevReportText, setPrevReportText] = useState('CBC Report: Hemoglobin 12.1 g/dL, WBC 5,800 /mcL, Platelets 190,000 /mcL, Fasting Blood Sugar 110 mg/dL.');
  const [prevReportDate, setPrevReportDate] = useState('2026-01-10');

  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!reportText.trim()) {
      setError('Please paste the lab report text to analyze.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setAnalysis(null);

      const previousReports = includeHistorical && prevReportText.trim() ? [
        {
          report_title: 'Historical CBC',
          report_date: prevReportDate,
          report_text: prevReportText
        }
      ] : [];

      const response = await ReportService.analyzeReport(
        reportText,
        reportTitle,
        reportDate,
        previousReports
      );

      if (response && response.data) {
        setAnalysis(response.data);
      } else {
        throw new Error('Invalid response structure received from Backend.');
      }
    } catch (err) {
      setError(err.message || 'Report analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {error && <Alert type="danger" title="Report Analysis Notice" message={error} />}

      <div className="grid-2">
        {/* Report Input Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <FileText style={{ color: 'var(--primary-600)' }} />
              <span>Medical Report Input</span>
            </div>
          </div>

          <form onSubmit={handleAnalyze}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Report Title</label>
                <input
                  type="text"
                  className="form-input"
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Report Date</label>
                <input
                  type="date"
                  className="form-input"
                  value={reportDate}
                  onChange={(e) => setReportDate(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Current Report Text / Measurements *</label>
              <textarea
                className="form-textarea"
                rows={4}
                value={reportText}
                onChange={(e) => setReportText(e.target.value)}
                placeholder="Paste lab report measurements e.g., Hemoglobin 14.2 g/dL, WBC 6500 /mcL..."
                required
              />
            </div>

            <div style={{ marginBottom: '16px', paddingTop: '12px', borderTop: '1px solid var(--border-color)' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.88rem', fontWeight: 600 }}>
                <input
                  type="checkbox"
                  checked={includeHistorical}
                  onChange={(e) => setIncludeHistorical(e.target.checked)}
                />
                <span>Include Historical Report for Trend Comparison</span>
              </label>

              {includeHistorical && (
                <div style={{ marginTop: '12px', padding: '12px', borderRadius: '8px', backgroundColor: 'var(--bg-surface-subtle)' }}>
                  <div className="form-group">
                    <label className="form-label">Historical Report Date</label>
                    <input type="date" className="form-input" value={prevReportDate} onChange={(e) => setPrevReportDate(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Historical Measurements Text</label>
                    <textarea className="form-textarea" rows={3} value={prevReportText} onChange={(e) => setPrevReportText(e.target.value)} />
                  </div>
                </div>
              )}
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px' }} disabled={loading}>
              <BarChart2 className="w-5 h-5" />
              <span>{loading ? 'Analyzing Clinical Parameters...' : 'Analyze Report & Parameters'}</span>
            </button>
          </form>
        </div>

        {/* Clinical Analysis Breakdown */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <TrendingUp style={{ color: 'var(--teal-600)' }} />
              <span>Clinical Analysis & Findings</span>
            </div>
            {analysis && <Badge type="neutral">{analysis.report_type || 'LAB REPORT'}</Badge>}
          </div>

          {loading ? (
            <LoadingSpinner label="Medical Report Agent extracting measured parameters and comparing clinical trends..." />
          ) : analysis ? (
            <div>
              {/* Executive Summary */}
              <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', marginBottom: '16px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary-700)', marginBottom: '4px' }}>Executive Clinical Summary:</div>
                <div style={{ fontSize: '0.88rem', color: 'var(--color-slate-800)' }}>{analysis.summary}</div>
              </div>

              {/* Extracted Measured Parameters */}
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px' }}>Extracted Parameters:</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
                {analysis.key_findings?.map((finding, idx) => (
                  <div key={idx} style={{
                    padding: '10px 14px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-surface-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    fontSize: '0.88rem'
                  }}>
                    <div>
                      <span style={{ fontWeight: 600 }}>{finding.parameter}</span>: <strong>{finding.value} {finding.unit}</strong>
                    </div>
                    <Badge type={finding.status === 'HIGH' || finding.status === 'ABNORMAL' ? 'high' : 'low'}>
                      {finding.status || 'NORMAL'}
                    </Badge>
                  </div>
                ))}
              </div>

              {/* Recommendations */}
              {analysis.recommendations?.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ fontSize: '0.88rem', fontWeight: 700, marginBottom: '6px' }}>Recommendations:</h4>
                  <ul style={{ paddingLeft: '20px', fontSize: '0.85rem', color: 'var(--color-slate-700)' }}>
                    {analysis.recommendations.map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--color-slate-500)' }}>
              <FileText style={{ width: '36px', height: '36px', opacity: 0.4, margin: '0 auto 12px auto' }} />
              <div>Submit report details on the left to view structured clinical summary and extracted test values.</div>
            </div>
          )}
        </div>
      </div>

      {/* Parameter Trend Visualization Section (Frontend Rendered Chart) */}
      {analysis && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <BarChart2 style={{ color: 'var(--primary-600)' }} />
              <span>Multi-Report Parameter Trend Visualization (Frontend Rendered)</span>
            </div>
          </div>

          {analysis.health_trends && analysis.health_trends.length > 0 ? (
            <div>
              <p style={{ fontSize: '0.88rem', color: 'var(--color-slate-600)', marginBottom: '16px' }}>
                Comparing overlapping parameters across historical reports. Chart dynamically rendered by Frontend Recharts engine.
              </p>

              <div className="grid-2">
                {analysis.health_trends.map((trend, i) => {
                  const chartData = trend.historical_values?.map((v, idx) => ({
                    date: v.date || `Point ${idx + 1}`,
                    value: parseFloat(v.value) || 0
                  })) || [];

                  return (
                    <div key={i} style={{ padding: '16px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-surface)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{trend.parameter} Trend</div>
                        <Badge type={trend.trend_direction === 'INCREASING' ? 'high' : 'low'}>{trend.trend_direction}</Badge>
                      </div>

                      <div style={{ width: '100%', height: 180 }}>
                        <ResponsiveContainer>
                          <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis dataKey="date" stroke="#64748b" style={{ fontSize: '0.75rem' }} />
                            <YAxis stroke="#64748b" style={{ fontSize: '0.75rem' }} />
                            <Tooltip />
                            <Line type="monotone" dataKey="value" stroke="#0284c7" strokeWidth={3} dot={{ r: 5 }} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <Alert type="info" title="Single Report Analysis">
              Only a single report was provided. Per healthcare audit standards, <strong>zero fake trends</strong> are generated for single-report analysis. Submit 2 or more historical reports to view parameter trend graphs.
            </Alert>
          )}

          <div style={{ fontSize: '0.78rem', color: 'var(--color-slate-500)', marginTop: '16px' }}>
            <strong>Medical Disclaimer:</strong> {analysis.disclaimer || 'Report analysis is for coordination guidance only and does not replace evaluation by a licensed physician.'}
          </div>
        </div>
      )}
    </div>
  );
};
