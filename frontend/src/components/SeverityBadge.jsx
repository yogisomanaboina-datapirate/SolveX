function SeverityBadge({ severity }) {
  const label =
    severity >= 5
      ? "CRITICAL"
      : severity >= 4
        ? "HIGH"
        : severity >= 3
          ? "MODERATE"
          : "LOW";

  return (
    <div className={`severity severity-${severity}`}>
      <span>●</span>
      Severity {severity}/5 — {label}
    </div>
  );
}

export default SeverityBadge;