function StatusTimeline({ currentStatus = "en_route" }) {
  const statuses = [
    ["dispatched", "Ambulance Dispatched"],
    ["en_route", "Ambulance En Route"],
    ["arrived", "Arrived at Patient"],
    ["hospital", "Hospital Arrival"],
  ];

  const currentIndex = statuses.findIndex(
    ([status]) => status === currentStatus,
  );

  return (
    <div className="timeline">
      {statuses.map(([status, label], index) => (
        <div
          className={`timeline-item ${
            index <= currentIndex ? "completed" : ""
          }`}
          key={status}
        >
          <div className="timeline-dot"></div>
          <span>{label}</span>
        </div>
      ))}
    </div>
  );
}

export default StatusTimeline;