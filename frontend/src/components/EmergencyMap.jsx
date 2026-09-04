function EmergencyMap({ ambulance, hospital }) {
  return (
    <section className="card tracking-card">
      <div className="map-header">
        <div>
          <span className="eyebrow">
            LIVE LOCATION
          </span>

          <h2>Ambulance Tracking</h2>
        </div>

        <span className="live-badge">
          ● LIVE
        </span>
      </div>

      <div className="map-card">
        <div className="map-grid"></div>

        <div className="map-overlay">
          <span className="map-label">
            LIVE EMERGENCY MAP
          </span>

          <div className="map-route"></div>

          <div className="map-marker ambulance-marker">
            🚑
            <span>
              {ambulance.id}
            </span>
          </div>

          <div className="map-marker hospital-marker">
            🏥
            <span>
              {hospital || "Hospital"}
            </span>
          </div>
        </div>
      </div>

      <div className="map-data-row">
        <div>
          <span className="label">
            Ambulance Location
          </span>

          <strong>
            {ambulance.location
              ? `${ambulance.location.lat.toFixed(5)}, ${ambulance.location.lng.toFixed(5)}`
              : "Updating..."}
          </strong>
        </div>

        <div>
          <span className="label">
            Current ETA
          </span>

          <strong>
            {ambulance.eta != null
              ? `${ambulance.eta} minutes`
              : "Updating..."}
          </strong>
        </div>
      </div>
    </section>
  );
}

export default EmergencyMap;