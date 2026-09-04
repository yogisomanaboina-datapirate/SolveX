function formatStatus(status) {
  switch (status) {
    case "dispatched":
      return "Dispatched";

    case "en_route":
      return "En Route";

    case "arrived":
      return "Arrived";

    case "hospital":
      return "At Hospital";

    default:
      return "Status Unavailable";
  }
}

function AmbulanceCard({ ambulance }) {
  return (
    <section className="card ambulance-card">
      <div className="card-heading">
        <div>
          <span className="eyebrow">AMBULANCE</span>

          <h2>
            {ambulance.id || "Not assigned"}
          </h2>
        </div>

        <span className="live-badge">
          LIVE
        </span>
      </div>

      <div className="ambulance-info">
        <div>
          <span className="label">Status</span>

          <strong>
            {formatStatus(ambulance.status)}
          </strong>
        </div>

        <div>
          <span className="label">ETA</span>

          <strong>
            {ambulance.eta != null
              ? `${ambulance.eta} min`
              : "Updating..."}
          </strong>
        </div>

        <div>
          <span className="label">Destination</span>

          <strong>
            {ambulance.hospitalName ||
              "Hospital not assigned"}
          </strong>
        </div>
      </div>
    </section>
  );
}

export default AmbulanceCard;