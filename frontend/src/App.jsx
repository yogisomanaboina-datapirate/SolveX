import { Navigate, Route, Routes } from "react-router-dom";

import Login from "./pages/Login";
import EmergencyInput from "./pages/EmergencyInput";
import EmergencyStatus from "./pages/EmergencyStatus";
import AmbulanceTracking from "./pages/AmbulanceTracking";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/emergency" element={<EmergencyInput />} />
      <Route path="/emergency/status" element={<EmergencyStatus />} />
      <Route
        path="/ambulance/:ambulanceId"
        element={<AmbulanceTracking />}
      />

      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;