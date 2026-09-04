import SeverityBadge from "./SeverityBadge";

function AIDecisionCard({ emergency }) {
  return (
    <section className="card ai-card">
      <div className="card-heading">
        <div>
          <span className="eyebrow">
            AI TRIAGE
          </span>

          <h2>Emergency Decision</h2>
        </div>

        <SeverityBadge
          severity={emergency.severity}
        />
      </div>

      <div className="decision-grid">
        <div>
          <span className="label">
            Detected Condition
          </span>

          <strong>
            {emergency.condition ||
              "Not available"}
          </strong>
        </div>

        <div>
          <span className="label">
            Recommended Action
          </span>

          <strong>
            {emergency.action ||
              "Not available"}
          </strong>
        </div>

        <div>
          <span className="label">
            Hospital
          </span>

          <strong>
            {emergency.hospitalName ||
              "Not assigned"}
          </strong>
        </div>

        <div>
          <span className="label">
            Ambulance ETA
          </span>

          <strong>
            {emergency.eta != null
              ? `${emergency.eta} minutes`
              : "Updating..."}
          </strong>
        </div>
      </div>

      {emergency.confidence != null && (
        <div className="confidence">
          <div>
            <span>AI Confidence</span>

            <strong>
              {emergency.confidence}%
            </strong>
          </div>

          <div className="confidence-bar">
            <div
              style={{
                width: `${Math.min(
                  100,
                  Math.max(
                    0,
                    emergency.confidence,
                  ),
                )}%`,
              }}
            ></div>
          </div>
        </div>
      )}

      {emergency.reasoning && (
        <div className="reasoning">
          <span className="label">
            AI Reasoning
          </span>

          <p>{emergency.reasoning}</p>
        </div>
      )}
    </section>
  );
}

export default AIDecisionCard;