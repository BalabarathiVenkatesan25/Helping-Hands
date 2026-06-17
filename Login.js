import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Login = ({ setUser }) => {
  const [role, setRole] = useState("donor");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    // Simulate successful login
    const loggedInUser = {
      name: role === "donor" ? "John Doe" : "Hope Orphanage",
      role: role,
    };

    setUser(loggedInUser);

    // Redirect to correct dashboard
    if (role === "donor") {
      navigate("/donor-dashboard");
    } else {
      navigate("/orphanage-dashboard");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-green-50 px-4">
      <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold text-green-700 text-center mb-6">
          {role === "donor" ? "Donor Login" : "Orphanage Login"}
        </h2>

        <div className="flex justify-center space-x-4 mb-6">
          <button
            onClick={() => setRole("donor")}
            className={`px-4 py-2 rounded-md ${
              role === "donor" ? "bg-green-600 text-white" : "bg-gray-200"
            }`}
          >
            Donor
          </button>
          <button
            onClick={() => setRole("orphanage")}
            className={`px-4 py-2 rounded-md ${
              role === "orphanage" ? "bg-green-600 text-white" : "bg-gray-200"
            }`}
          >
            Orphanage
          </button>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            className="w-full border rounded-md p-3"
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full border rounded-md p-3"
          />
          <button
            type="submit"
            className="w-full bg-green-600 text-white py-3 rounded-md"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
