import React, { useState } from "react";
import { useRequests } from "../context/RequestContext";
import "../dashboard.css"; // adjust path based on your folder structure

export default function DonorDashboard() {
  const { requests, donations, donateToRequest } = useRequests();
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [donorName, setDonorName] = useState("");
  const [donorPhone, setDonorPhone] = useState("");
  const [donorAddress, setDonorAddress] = useState("");

  const handleDonate = () => {
    if (!donorName || !donorPhone || !donorAddress) {
      alert("Please fill all donor details.");
      return;
    }
    donateToRequest(selectedRequest.id, donorName, donorPhone, donorAddress);
    setSelectedRequest(null);
    alert("Donation Completed!");
  };

  return (
    <div className="dashboard-container">
      <h1>Donor Dashboard</h1>

      {/* Available Requests */}
      <div className="list">
        <h2>Available Orphanage Requests</h2>
        <ul>
          {requests
            .filter((r) => r.status === "Pending")
            .map((req) => (
              <li key={req.id} className="list-item">
                <div className="request-info">
                  <p>
                    <strong>Orphanage:</strong> {req.orphanageName}
                  </p>
                  <p>
                    <strong>Type:</strong> {req.requestType}
                  </p>
                  <p>
                    <strong>Quantity:</strong> {req.quantity}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedRequest(req)}
                  className="button"
                >
                  Donate
                </button>
              </li>
            ))}
        </ul>
      </div>

      {/* Donation Form */}
      {selectedRequest && (
        <div className="list">
          <h3>Complete Your Donation</h3>
          <div className="form-group">
            <input
              type="text"
              placeholder="Your Name"
              value={donorName}
              onChange={(e) => setDonorName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              placeholder="Your Phone"
              value={donorPhone}
              onChange={(e) => setDonorPhone(e.target.value)}
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              placeholder="Your Address"
              value={donorAddress}
              onChange={(e) => setDonorAddress(e.target.value)}
            />
          </div>
          <button onClick={handleDonate} className="button button-green">
            Confirm Donation
          </button>
        </div>
      )}

      {/* Donation History */}
      <div className="list">
        <h2>Donation History</h2>
        <ul>
          {donations.map((d, idx) => (
            <li key={idx} className="list-item">
              <div className="request-info">
                <p>
                  <strong>Orphanage:</strong> {d.orphanageName}
                </p>
                <p>
                  <strong>Type:</strong> {d.type}
                </p>
                <p>
                  <strong>Quantity:</strong> {d.quantity}
                </p>
                <p
                  className={
                    d.status === "Completed"
                      ? "status-completed"
                      : "status-pending"
                  }
                >
                  <strong>Status:</strong> {d.status}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
