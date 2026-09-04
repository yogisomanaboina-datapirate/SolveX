import React, { useState, useEffect } from 'react';
import { Pill, Clock, AlertTriangle, Plus, Trash2, CheckCircle2, Info, Bell, BellRing, Sparkles } from 'lucide-react';
import { Badge, Alert, LoadingSpinner } from '../components/CommonUI';
import { MedicationService, NotificationService } from '../api/services';
import { requestNotificationPermission, onForegroundMessage } from '../config/firebase';

export const Medications = () => {
  const [medList, setMedList] = useState([
    { name: 'Amoxicillin', dosage: '500mg', frequency: 'Three times daily', mealRelationship: 'AFTER_MEAL', durationDays: 5 },
    { name: 'Paracetamol', dosage: '500mg', frequency: 'Twice daily', mealRelationship: 'AFTER_MEAL', durationDays: 3 }
  ]);

  const [wakeTime, setWakeTime] = useState('08:00');
  const [sleepTime, setSleepTime] = useState('22:00');
  
  const [loading, setLoading] = useState(false);
  const [scheduleResult, setScheduleResult] = useState(null);
  const [error, setError] = useState(null);

  // FCM Notification States
  const [notifPermission, setNotifPermission] = useState(
    typeof Notification !== 'undefined' ? Notification.permission : 'default'
  );
  const [registeredToken, setRegisteredToken] = useState(null);
  const [foregroundToast, setForegroundToast] = useState(null);
  const [demoLoading, setDemoLoading] = useState(false);

  useEffect(() => {
    // Auto-request or register notification token if permission is already granted
    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      handleEnableNotifications();
    }

    // Subscribe to foreground FCM push messages
    const unsubscribe = onForegroundMessage((payload) => {
      const title = payload.notification?.title || payload.data?.title || 'Medication Reminder';
      const body = payload.notification?.body || payload.data?.body || 'Time to take your scheduled medication.';
      setForegroundToast({ title, body, timestamp: new Date().toLocaleTimeString() });
    });

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, []);

  const handleEnableNotifications = async () => {
    try {
      const token = await requestNotificationPermission();
      if (token) {
        setRegisteredToken(token);
        setNotifPermission('granted');
        await NotificationService.registerToken(token);
      }
    } catch (err) {
      console.warn('FCM registration notice:', err);
    }
  };

  const handleScheduleDemoReminder = async () => {
    try {
      setDemoLoading(true);
      setError(null);
      await NotificationService.scheduleDemoReminder('Amoxicillin (Demo)', '500mg', 60);
      alert('1-Minute Demo Reminder Scheduled! APScheduler will dispatch FCM Push Notification in ~60 seconds.');
    } catch (err) {
      setError('Failed to schedule demo reminder.');
    } finally {
      setDemoLoading(false);
    }
  };

  const handleAddMedication = () => {
    setMedList([...medList, { name: '', dosage: '', frequency: 'Twice daily', mealRelationship: 'AFTER_MEAL', durationDays: 5 }]);
  };

  const handleRemoveMedication = (index) => {
    setMedList(medList.filter((_, i) => i !== index));
  };

  const handleMedChange = (index, field, value) => {
    const updated = [...medList];
    updated[index][field] = value;
    setMedList(updated);
  };

  const handleGenerateSchedule = async (e) => {
    e.preventDefault();
    const validMeds = medList.filter((m) => m.name.trim() !== '');
    if (validMeds.length === 0) {
      setError('Please add at least one medication name.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setScheduleResult(null);

      const response = await MedicationService.generateSchedule(validMeds, wakeTime, sleepTime);
      if (response && response.data) {
        setScheduleResult(response.data);
      } else {
        throw new Error('Invalid response structure received from Backend.');
      }
    } catch (err) {
      setError(err.message || 'Failed to generate medication schedule.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* FCM Push Notification Permission & Status Bar */}
      <div className="card" style={{ marginBottom: '16px', padding: '14px 18px', backgroundColor: '#f8fafc', border: '1px solid #cbd5e1' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BellRing style={{ color: notifPermission === 'granted' ? '#16a34a' : '#d97706', width: '20px', height: '20px' }} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>
                Firebase Cloud Messaging (FCM) Push Notifications: {notifPermission === 'granted' ? 'ACTIVE & CONNECTED' : 'PERMISSON REQUIRED'}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--color-slate-600)' }}>
                {registeredToken ? `FCM Web Identifier: ${registeredToken.substring(0, 24)}...` : 'Enable browser push notifications to receive real-time medication reminders.'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            {notifPermission !== 'granted' && (
              <button type="button" className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={handleEnableNotifications}>
                <Bell className="w-4 h-4" /> Enable Browser Notifications
              </button>
            )}
            <button type="button" className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem', backgroundColor: '#e0f2fe', color: '#0369a1', borderColor: '#7dd3fc' }} onClick={handleScheduleDemoReminder} disabled={demoLoading}>
              <Sparkles className="w-4 h-4" /> {demoLoading ? 'Scheduling...' : 'Schedule 1-Min Demo Push'}
            </button>
          </div>
        </div>
      </div>

      {/* Foreground FCM Toast Notification */}
      {foregroundToast && (
        <Alert type="success" title={`FCM Push Received (${foregroundToast.timestamp})`}>
          <strong>{foregroundToast.title}:</strong> {foregroundToast.body}
        </Alert>
      )}

      {error && <Alert type="danger" title="Schedule Notice" message={error} />}

      <div className="grid-2">
        {/* Prescription Input Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Pill style={{ color: 'var(--primary-600)' }} />
              <span>Doctor Prescriptions Input</span>
            </div>
            <button type="button" className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={handleAddMedication}>
              <Plus className="w-4 h-4" /> Add Med
            </button>
          </div>

          <form onSubmit={handleGenerateSchedule}>
            {medList.map((med, idx) => (
              <div key={idx} style={{
                padding: '14px',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                marginBottom: '12px',
                backgroundColor: 'var(--bg-surface-subtle)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-slate-700)' }}>Medication #{idx + 1}</span>
                  {medList.length > 1 && (
                    <button type="button" onClick={() => handleRemoveMedication(idx)} style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer' }}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Medication Name</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. Amoxicillin"
                      value={med.name}
                      onChange={(e) => handleMedChange(idx, 'name', e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Dosage</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. 500mg"
                      value={med.dosage}
                      onChange={(e) => handleMedChange(idx, 'dosage', e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Frequency</label>
                    <select className="form-select" value={med.frequency} onChange={(e) => handleMedChange(idx, 'frequency', e.target.value)}>
                      <option value="Once daily">Once daily</option>
                      <option value="Twice daily">Twice daily</option>
                      <option value="Three times daily">Three times daily</option>
                      <option value="Every 8 hours">Every 8 hours</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Meal Relationship</label>
                    <select className="form-select" value={med.mealRelationship} onChange={(e) => handleMedChange(idx, 'mealRelationship', e.target.value)}>
                      <option value="AFTER_MEAL">After Meal</option>
                      <option value="BEFORE_MEAL">Before Meal</option>
                      <option value="WITH_FOOD">With Food</option>
                      <option value="ANYTIME">Anytime</option>
                    </select>
                  </div>
                </div>
              </div>
            ))}

            <div className="grid-2" style={{ marginTop: '16px', marginBottom: '16px' }}>
              <div className="form-group">
                <label className="form-label">Wake Time</label>
                <input type="time" className="form-input" value={wakeTime} onChange={(e) => setWakeTime(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Sleep Time</label>
                <input type="time" className="form-input" value={sleepTime} onChange={(e) => setSleepTime(e.target.value)} />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px' }} disabled={loading}>
              <Clock className="w-5 h-5" />
              <span>{loading ? 'AI Conflict Detection & Scheduling...' : 'Generate Conflict-Checked Schedule'}</span>
            </button>
          </form>
        </div>

        {/* Schedule & Conflict Output */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Clock style={{ color: 'var(--teal-600)' }} />
              <span>Daily Timeline & Conflict Analysis</span>
            </div>
            {scheduleResult && (
              <Badge type={scheduleResult.hasConflicts ? 'high' : 'low'}>
                {scheduleResult.hasConflicts ? 'Conflicts Detected' : 'Conflict Free'}
              </Badge>
            )}
          </div>

          {loading ? (
            <LoadingSpinner label="AI Medication Scheduler calculating intake times and checking timing overlaps..." />
          ) : scheduleResult ? (
            <div>
              {/* Conflict Warnings */}
              {scheduleResult.hasConflicts && scheduleResult.conflictsDetected?.length > 0 && (
                <Alert type="warning" title="Timing Conflict Warning">
                  {scheduleResult.conflictsDetected.map((c, i) => (
                    <div key={i} style={{ fontSize: '0.85rem', marginTop: '4px' }}>
                      • <strong>{c.conflict_type}:</strong> {c.description} — <em>{c.resolution_recommendation}</em>
                    </div>
                  ))}
                </Alert>
              )}

              {/* Reminders Timeline */}
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '12px' }}>Chronological Intake Reminders:</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
                {scheduleResult.scheduledReminders?.map((r, i) => (
                  <div key={i} style={{
                    padding: '12px 14px',
                    borderRadius: '8px',
                    backgroundColor: '#f0f9ff',
                    border: '1px solid #bae6fd',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--color-slate-900)' }}>
                        {r.medication_name} ({r.dosage})
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--color-slate-600)', marginTop: '2px' }}>
                        {r.instructions} • {r.meal_relation_note}
                      </div>
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--primary-700)', backgroundColor: '#ffffff', padding: '6px 12px', borderRadius: '6px', border: '1px solid #bae6fd' }}>
                      {r.scheduled_time}
                    </div>
                  </div>
                ))}
              </div>

              {/* AI Disclaimer */}
              <div style={{ fontSize: '0.78rem', color: 'var(--color-slate-500)', backgroundColor: 'var(--bg-surface-subtle)', padding: '10px', borderRadius: '6px' }}>
                <strong>Safety Disclaimer:</strong> {scheduleResult.disclaimer}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--color-slate-500)' }}>
              <Pill style={{ width: '36px', height: '36px', opacity: 0.4, margin: '0 auto 12px auto' }} />
              <div>Enter prescribed medications on the left to generate an optimal conflict-checked intake schedule.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
