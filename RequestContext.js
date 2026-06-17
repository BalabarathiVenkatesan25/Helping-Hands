import React, { createContext, useContext, useState } from "react";

const RequestContext = createContext();

export const RequestProvider = ({ children }) => {
  const [requests, setRequests] = useState([]);
  const [donations, setDonations] = useState([]);
  const [contacts, setContacts] = useState([]); // donor details for orphanage

  // Orphanage creates request
  const addRequest = (orphanageName, requestType, quantity) => {
    const newRequest = {
      id: Date.now(),
      orphanageName,
      requestType,
      quantity,
      status: "Pending",
    };
    setRequests((prev) => [...prev, newRequest]);
  };

  // Donor donates to request
  const donateToRequest = (requestId, donorName, donorPhone, donorAddress) => {
    setRequests((prev) =>
      prev.map((req) =>
        req.id === requestId ? { ...req, status: "Completed" } : req
      )
    );

    const request = requests.find((r) => r.id === requestId);
    if (request) {
      const donationEntry = {
        id: Date.now(),
        orphanageName: request.orphanageName,
        type: request.requestType,
        quantity: request.quantity,
        status: "Completed",
      };
      setDonations((prev) => [...prev, donationEntry]);

      const contactEntry = {
        id: Date.now(),
        orphanageName: request.orphanageName,
        donorName,
        donorPhone,
        donorAddress,
      };
      setContacts((prev) => [...prev, contactEntry]);
    }
  };

  return (
    <RequestContext.Provider
      value={{
        requests,
        donations,
        contacts,
        addRequest,
        donateToRequest,
      }}
    >
      {children}
    </RequestContext.Provider>
  );
};

export const useRequests = () => useContext(RequestContext);
