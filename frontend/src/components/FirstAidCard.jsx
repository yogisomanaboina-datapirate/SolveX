function FirstAidCard({ instructions = [] }) {
  return (
    <section className="card first-aid-card">
      <span className="eyebrow">
        WHILE HELP IS COMING
      </span>

      <h2>Immediate First Aid</h2>

      {instructions.length > 0 ? (
        <div className="first-aid-list">
          {instructions.map(
            (instruction, index) => (
              <div
                className="first-aid-item"
                key={`${instruction}-${index}`}
              >
                <span>{index + 1}</span>

                <p>{instruction}</p>
              </div>
            ),
          )}
        </div>
      ) : (
        <p className="empty-state">
          First-aid instructions are not
          currently available.
        </p>
      )}
    </section>
  );
}

export default FirstAidCard;