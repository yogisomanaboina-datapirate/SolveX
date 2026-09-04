import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Header from "../components/Header";
import EmergencyMap from "../components/EmergencyMap";
import AmbulanceCard from "../components/AmbulanceCard";
import StatusTimeline from "../components/StatusTimeline";

import {
  getAmbulance,
  subscribeToAmbulance,
} from "../services/ambulanceService";

function AmbulanceTracking() {
  const { ambulanceId } = useParams();
  const navigate = useNavigate();

  const [ambulance, setAmbulance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let unsubscribe = () => {};

    const loadAmbulance = async () => {
      try {
        const response =
          await getAmbulance(ambulanceId);

        setAmbulance(response.data);

        unsubscribe =
          subscribeToAmbulance(
            ambulanceId,
            setAmbulance,
          );
      } catch (requestError) {
        console.error(requestError);

        setError(
          requestError.message ||
            "Unable to load ambulance information.",
        );
      } finally {
        setLoading(false);
      }
    };

    loadAmbulance();

    return () => unsubscribe();
  }, [ambulanceId]);

  if (loading) {
    return (
      <div className="app-shell">
        <Header />

        <main className="page-container">
          <div className="card loading-card">
            Loading ambulance tracking...
          </div>
        </main>
      </div>
    );
  }

  if (error || !ambulance) {
    return (
      <div className="app-shell">
        <Header />

        <main className="page-container">
          <div className="card error-card">
            <strong>Tracking unavailable</strong>
            <p>
              {error ||
                "No ambulance information is available."}
            </p>

            <button
              className="secondary-button"
              onClick={() =>
                navigate("/emergency/status")
              }
            >
              Back to Emergency Status
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Header />

      <main className="page-container">
        <div className="workflow-progress">
          <span className="workflow-step completed">
            ✓ Emergency
          </span>

          <span className="workflow-line active"></span>

          <span className="workflow-step completed">
            ✓ AI Response
          </span>

          <span className="workflow-line active"></span>

          <span className="workflow-step active">
            3. Tracking
          </span>
        </div>

        <div className="page-title">
          <span className="eyebrow">
            LIVE AMBULANCE TRACKING
          </span>

          <h1>Your ambulance is on the way.</h1>

          <p>
            Location and response status are updated from
            the ambulance tracking service.
          </p>
        </div>

        <AmbulanceCard ambulance={ambulance} />

        <EmergencyMap
          ambulance={ambulance}
          hospital={ambulance.hospitalName}
        />

        <StatusTimeline
          currentStatus={ambulance.status}
        />

        <button
          className="secondary-button"
          onClick={() =>
            navigate("/emergency/status")
          }
        >
          ← Back to Emergency Status
        </button>
      </main>
    </div>
  );
}

export default AmbulanceTracking;