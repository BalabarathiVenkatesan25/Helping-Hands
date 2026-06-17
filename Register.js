import React, { useState } from "react";

const Register = () => {
  const [role, setRole] = useState("donor");

  return (
    <div className="min-h-screen flex items-center justify-center bg-green-50 px-4">
      <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold text-green-700 text-center mb-6">
          {role === "donor" ? "Donor Registration" : "Orphanage Registration"}
        </h2>

        {/* Role Toggle */}
        <div className="flex justify-center space-x-4 mb-6">
          <button
            onClick={() => setRole("donor")}
            className={`px-4 py-2 rounded-md font-medium ${
              role === "donor"
                ? "bg-green-600 text-white"
                : "bg-gray-200 text-gray-700"
            }`}
          >
            Donor
          </button>
          <button
            onClick={() => setRole("orphanage")}
            className={`px-4 py-2 rounded-md font-medium ${
              role === "orphanage"
                ? "bg-green-600 text-white"
                : "bg-gray-200 text-gray-700"
            }`}
          >
            Orphanage
          </button>
        </div>

        {/* Registration Form */}
        <form className="space-y-4">
          {role === "orphanage" && (
            <input
              type="text"
              placeholder="Orphanage Name"
              className="w-full border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          )}
          {role === "donor" && (
            <input
              type="text"
              placeholder="Full Name"
              className="w-full border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          )}
          <input
            type="email"
            placeholder="Email"
            className="w-full border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <input
            type="password"
            placeholder="Confirm Password"
            className="w-full border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <input
            type="text"
            placeholder="Phone Number"
            className="w-full border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          {role === "orphanage" && (
            <textarea
              placeholder="Address"
              className="w-full border border-gray-300 rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
            ></textarea>
          )}
          <button
            type="submit"
            className="w-full bg-green-600 text-white py-3 rounded-md hover:bg-green-700"
          >
            Register
          </button>
        </form>

        {/* Links */}
        <div className="text-center mt-4">
          <a href="/login" className="text-green-600 hover:underline">
            Already have an account? Login
          </a>
        </div>
      </div>
    </div>
  );
};

export default Register;
