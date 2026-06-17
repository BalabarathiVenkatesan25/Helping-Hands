import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { RequestProvider } from "./context/RequestContext";
import './index.css';


const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <RequestProvider>
      <App />
    </RequestProvider>
  </React.StrictMode>
);
