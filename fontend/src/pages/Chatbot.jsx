import React, { useState } from 'react';
import { MessageSquareHeart, Send, Bot, User, Siren, ShieldAlert, Sparkles, AlertCircle } from 'lucide-react';
import { Badge, Alert, LoadingSpinner } from '../components/CommonUI';
import { ChatService } from '../api/services';

export const Chatbot = ({ setActiveTab }) => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your LifeLink AI Health Assistant. I can answer health queries, explain lab reports, check scheduled medications, or review insurance claim status. How can I assist you today?',
      intent: 'GENERAL_HEALTH_QUERY',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputMsg, setInputMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sampleQueries = [
    'What is hemoglobin?',
    'What was my latest hemoglobin level?',
    'What medications are scheduled for me?',
    'What is the status of my insurance claim?',
    'I am experiencing severe chest pain and shortness of breath!'
  ];

  const handleSendMessage = async (textToSend) => {
    const queryText = textToSend || inputMsg;
    if (!queryText.trim()) return;

    const userMsg = {
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMsg('');

    try {
      setLoading(true);
      setError(null);

      // Authorized patient profile context supplied by Backend gateway
      const patientProfile = {
        patient_name: 'Demo Patient',
        latest_lab_results: { Hemoglobin: '14.2 g/dL', WBC: '6,500 /mcL', Glucose: '95 mg/dL' },
        medications: [{ name: 'Amoxicillin', dosage: '500mg', schedule: '08:00, 20:00' }],
        claims: [{ claim_id: 'CLM-992', status: 'APPROVED', amount: 15000 }]
      };

      const historyPayload = messages.map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text
      }));

      const response = await ChatService.sendMessage(queryText, patientProfile, historyPayload);

      if (response && response.data) {
        const botData = response.data;
        const botMsg = {
          sender: 'bot',
          text: botData.message || botData.reply || botData.response_text || 'No response generated.',
          intent: botData.intent,
          personalizedDataUsed: botData.personalized_data_used || botData.personalizedDataUsed,
          emergencyDetected: botData.emergency_detected || botData.emergencyDetected || botData.intent === 'EMERGENCY_GUIDANCE',
          suggestedFollowups: botData.suggested_quick_actions || botData.suggested_followups || [],
          disclaimer: botData.disclaimer,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setMessages((prev) => [...prev, botMsg]);
      } else {
        throw new Error('Invalid chat response from Backend.');
      }
    } catch (err) {
      setError(err.message || 'AI Assistant connection timed out.');
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: 'I am operating in safety fallback mode. Please consult your medical provider for specific clinical questions.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 140px)' }}>
      {/* Sample Quick Questions Bar */}
      <div style={{ marginBottom: '14px', display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
        <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-slate-500)', alignSelf: 'center', whiteSpace: 'nowrap' }}>Suggested Queries:</span>
        {sampleQueries.map((q, idx) => (
          <button
            key={idx}
            type="button"
            className="btn btn-secondary"
            style={{ padding: '4px 10px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
            onClick={() => handleSendMessage(q)}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat Messages Log Container */}
      <div className="card" style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '14px', padding: '20px' }}>
        {messages.map((m, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              gap: '12px',
              justifyContent: m.sender === 'user' ? 'flex-end' : 'flex-start'
            }}
          >
            {m.sender === 'bot' && (
              <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: '#f0f9ff', color: 'var(--primary-600)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #bae6fd', flexShrink: 0 }}>
                <Bot className="w-5 h-5" />
              </div>
            )}

            <div style={{
              maxWidth: '75%',
              padding: '14px 16px',
              borderRadius: '12px',
              backgroundColor: m.sender === 'user' ? 'var(--primary-600)' : 'var(--bg-surface-subtle)',
              color: m.sender === 'user' ? '#ffffff' : 'var(--color-slate-900)',
              border: m.sender === 'user' ? 'none' : '1px solid var(--border-color)',
              fontSize: '0.92rem'
            }}>
              {/* Emergency Detected Banner inside message */}
              {m.emergencyDetected && (
                <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', padding: '10px 12px', borderRadius: '8px', marginBottom: '10px', color: '#b91c1c', fontSize: '0.85rem' }}>
                  <div style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Siren className="w-4 h-4" /> EMERGENCY SYMPTOMS DETECTED
                  </div>
                  <div style={{ marginTop: '4px' }}>AI routed query to Emergency Assistance protocol.</div>
                  <button
                    className="btn btn-emergency"
                    style={{ marginTop: '8px', padding: '4px 10px', fontSize: '0.78rem' }}
                    onClick={() => setActiveTab('emergency')}
                  >
                    Go to Emergency Triage
                  </button>
                </div>
              )}

              <div>{m.text}</div>

              {/* Context Badges & Followups */}
              {m.sender === 'bot' && (
                <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(0,0,0,0.06)', display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center', fontSize: '0.75rem', color: 'var(--color-slate-500)' }}>
                  {m.intent && <Badge type="neutral">Intent: {m.intent}</Badge>}
                  {m.personalizedDataUsed && <Badge type="low">Profile Data Used</Badge>}
                  <span style={{ marginLeft: 'auto' }}>{m.timestamp}</span>
                </div>
              )}
            </div>

            {m.sender === 'user' && (
              <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'var(--color-slate-800)', color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <User className="w-5 h-5" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', color: 'var(--color-slate-500)', fontSize: '0.88rem' }}>
            <Bot className="w-5 h-5 animate-pulse text-sky-600" />
            <span>AI Assistant thinking...</span>
          </div>
        )}
      </div>

      {/* Message Input Box */}
      <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          className="form-input"
          style={{ flex: 1, padding: '12px 16px' }}
          placeholder="Ask a health query or inquire about your medical reports..."
          value={inputMsg}
          onChange={(e) => setInputMsg(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '0 20px' }} disabled={loading || !inputMsg.trim()}>
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};
