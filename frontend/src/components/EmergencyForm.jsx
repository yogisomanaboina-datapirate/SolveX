import { useState } from "react";

import VoiceInput from "./VoiceInput";
import LocationCapture from "./LocationCapture";

function EmergencyForm({ onSubmit, loading = false }) {
  const [symptoms, setSymptoms] = useState("");
  const [emergencyType, setEmergencyType] = useState("cardiac");
  const [location, setLocation] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();

    onSubmit({
      symptoms: symptoms.trim(),
      emergencyType,
      location,
    });
  };

  return (
    <form className="card emergency-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <span className="eyebrow">EMERGENCY INPUT</span>

        <h1>Tell us what is happening</h1>

        <p>
          Describe the emergency clearly. You can type your symptoms
          or use your voice.
        </p>
      </div>

      <label>
        Emergency Type

        <select
          value={emergencyType}
          onChange={(event) =>
            setEmergencyType(event.target.value)
          }
          disabled={loading}
        >
          <option value="cardiac">Cardiac</option>
          <option value="respiratory">Respiratory</option>
          <option value="trauma">Trauma</option>
          <option value="other">Other</option>
        </select>
      </label>

      <label>
        Symptoms

        <textarea
          value={symptoms}
          onChange={(event) =>
            setSymptoms(event.target.value)
          }
          placeholder="Example: Chest pain, difficulty breathing..."
          rows="6"
          required
          disabled={loading}
        />
      </label>

      <VoiceInput
        onTranscript={setSymptoms}
        disabled={loading}
      />

      <LocationCapture
        location={location}
        onCapture={setLocation}
        disabled={loading}
      />

      <button
        className="primary-button submit-emergency-button"
        type="submit"
        disabled={loading}
      >
        {loading
          ? "Analyzing Emergency..."
          : "🚨 Request Emergency Assistance"}
      </button>

      <p className="form-note">
        Your symptoms and location are used to coordinate the emergency
        response.
      </p>
    </form>
  );
}

export default EmergencyForm;