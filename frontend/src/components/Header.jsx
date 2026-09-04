function Header() {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-mark">
          S
        </div>

        <div>
          <h2>SolveX</h2>

          <span>
            Emergency Response
          </span>
        </div>
      </div>

      <div className="system-status">
        <span className="status-dot"></span>
        Emergency System Online
      </div>
    </header>
  );
}

export default Header;