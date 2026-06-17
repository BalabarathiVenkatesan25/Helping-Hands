import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import DonorDashboard from "./pages/DonorDashboard";
import OrphanageDashboard from "./pages/OrphanageDashboard";
import { useState } from "react";

function App() {
  const [user, setUser] = useState(null); // store logged-in user details

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login setUser={setUser} />} />

        {/* Role-based dashboard */}
        <Route
          path="/donor-dashboard"
          element={
            user?.role === "donor" ? (
              <DonorDashboard user={user} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/orphanage-dashboard"
          element={
            user?.role === "orphanage" ? (
              <OrphanageDashboard user={user} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
