import { useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  return (
    <main className="login-page">
      <div className="login-hero">
        <div className="logo-large">S</div>

        <span className="eyebrow">SOLVEX EMERGENCY NETWORK</span>

        <h1>Emergency response,<br />connected.</h1>

        <p>
          AI-powered triage, intelligent ambulance dispatch,
          and real-time hospital coordination.
        </p>

        <button
          className="primary-button login-button"
          onClick={() => navigate("/emergency")}
        >
          Enter Emergency System →
        </button>

        <div className="trust-row">
          <span>● AI Triage</span>
          <span>● Live Ambulance</span>
          <span>● Hospital Coordination</span>
        </div>
      </div>
    </main>
  );
}

export default Login;