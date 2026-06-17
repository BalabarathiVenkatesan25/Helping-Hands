import React from "react";

const Navbar = ({ title }) => {
  return (
    <nav className="bg-white shadow-md py-4 px-6 flex justify-between items-center border-b">
      <h1 className="text-2xl font-bold text-green-600">{title}</h1>
      <button
        onClick={() => window.location.href = "/login"}
        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
      >
        Logout
      </button>
    </nav>
  );
};

export default Navbar;
