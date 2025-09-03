import React, { useState } from "react";
import { useRequests } from "../context/RequestContext";
import "../dashboard.css"; // adjust path based on your folder structure

export default function OrphanageDashboard() {
  const { requests, contacts, addRequest } = useRequests();
  const [orphanageName, setOrphanageName] = useState("");
  const [requestType, setRequestType] = useState("Food");
  const [quantity, setQuantity] = useState("");

  const handleRequest = () => {
    if (!orphanageName || !quantity) {
      alert("Fill all request details");
      return;
    }
    addRequest(orphanageName, requestType, quantity);
    alert("Request submitted!");
    setOrphanageName("");
    setQuantity("");
  };

  return (
    <div className="dashboard-container">
      <h1>Orphanage Dashboard</h1>

      {/* Create Request */}
      <div className="list">
        <h2>Create Request</h2>
        <div className="form-group">
          <input
            type="text"
            placeholder="Orphanage Name"
            value={orphanageName}
            onChange={(e) => setOrphanageName(e.target.value)}
          />
        </div>
        <div className="form-group">
          <select
            value={requestType}
            onChange={(e) => setRequestType(e.target.value)}
          >
            <option>Food</option>
            <option>Clothes</option>
            <option>Education</option>
            <option>Fund</option>
          </select>
        </div>
        <div className="form-group">
          <input
            type="number"
            placeholder="Quantity"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
        </div>
        <button onClick={handleRequest} className="button">
          Submit Request
        </button>
      </div>

      {/* Request History */}
      <div className="list">
        <h2>Request History</h2>
        <ul>
          {requests.map((r) => (
            <li key={r.id} className="list-item">
              <div className="request-info">
                <p>
                  <strong>Type:</strong> {r.requestType}
                </p>
                <p>
                  <strong>Quantity:</strong> {r.quantity}
                </p>
                <p
                  className={
                    r.status === "Completed" ? "status-completed" : "status-pending"
                  }
                >
                  <strong>Status:</strong> {r.status}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Donor Contacts */}
      <div className="list">
        <h2>Donor Contact Details</h2>
        <ul>
          {contacts.map((c) => (
            <li key={c.id} className="list-item">
              <div className="contact-box">
                <p>
                  <strong>Donor:</strong> {c.donorName}
                </p>
                <p>
                  <strong>Phone:</strong> {c.donorPhone}
                </p>
                <p>
                  <strong>Address:</strong> {c.donorAddress}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
