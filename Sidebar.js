import React from "react";
import { Link, useLocation } from "react-router-dom";

const Sidebar = ({ role }) => {
  const location = useLocation();

  const donorLinks = [
    { path: "/donor-dashboard", label: "Dashboard" },
    { path: "/donations", label: "My Donations" },
    { path: "/orphanages", label: "Find Orphanages" },
  ];

  const orphanageLinks = [
    { path: "/orphanage-dashboard", label: "Dashboard" },
    { path: "/requests", label: "My Requests" },
    { path: "/donors", label: "Find Donors" },
  ];

  const links = role === "donor" ? donorLinks : orphanageLinks;

  return (
    <aside className="bg-green-700 text-white w-64 min-h-screen p-6">
      <h2 className="text-lg font-bold mb-6">Menu</h2>
      <ul className="space-y-4">
        {links.map((link, idx) => (
          <li key={idx}>
            <Link
              to={link.path}
              className={`block px-3 py-2 rounded-md ${
                location.pathname === link.path
                  ? "bg-green-900"
                  : "hover:bg-green-600"
              }`}
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default Sidebar;
