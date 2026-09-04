import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Header from "../components/Header";
import EmergencyForm from "../components/EmergencyForm";
import { submitEmergency } from "../services/emergencyService";

function EmergencyInput() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleEmergency = async (emergencyRequest) => {
    setLoading(true);
    setError("");

    try {
      const response = await submitEmergency(emergencyRequest);

      sessionStorage.setItem(
        "emergencyData",
        JSON.stringify(response.data),
      );

      navigate("/emergency/status");
    } catch (requestError) {
      console.error(requestError);

      setError(
        requestError.message ||
          "Unable to submit the emergency. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Header />

      <main className="page-container">
        <div className="workflow-progress">
          <span className="workflow-step active">1. Emergency</span>
          <span className="workflow-line"></span>
          <span className="workflow-step">2. AI Response</span>
          <span className="workflow-line"></span>
          <span className="workflow-step">3. Tracking</span>
        </div>

        {error && (
          <div className="card error-card">
            <strong>Emergency submission failed</strong>
            <p>{error}</p>
          </div>
        )}

        <EmergencyForm
          onSubmit={handleEmergency}
          loading={loading}
        />
      </main>
    </div>
  );
}

export default EmergencyInput;