import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import AIDecisionCard from "../components/AIDecisionCard";
import FirstAidCard from "../components/FirstAidCard";
import AmbulanceCard from "../components/AmbulanceCard";
import { mockEmergency, mockAmbulance } from "../data/mockData";

function EmergencyStatus() {
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <Header />

      <main className="page-container">
        <div className="page-title">
          <span className="eyebrow">EMERGENCY ACTIVE</span>

          <h1>Help is on the way.</h1>

          <p>
            Our AI has analyzed your emergency and coordinated
            the response.
          </p>
        </div>

        <AIDecisionCard emergency={mockEmergency} />

        <div className="two-column">
          <FirstAidCard instructions={mockEmergency.firstAid} />

          <AmbulanceCard ambulance={mockAmbulance} />
        </div>

        <button
          className="primary-button"
          onClick={() =>
            navigate(`/ambulance/${mockEmergency.ambulanceId}`)
          }
        >
          Track Ambulance →
        </button>
      </main>
    </div>
  );
}

export default EmergencyStatus;