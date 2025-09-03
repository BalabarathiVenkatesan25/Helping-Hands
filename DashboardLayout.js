import React from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

const DashboardLayout = ({ title, role, children }) => {
  return (
    <div className="flex min-h-screen bg-green-50">
      <Sidebar role={role} />
      <div className="flex flex-col flex-1">
        <Navbar title={title} />
        <main className="p-6 flex-1">{children}</main>
      </div>
    </div>
  );
};

export default DashboardLayout;
