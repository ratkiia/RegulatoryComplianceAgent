import React from "react";
import { Link, Route, Routes } from "react-router-dom";

function DashboardPage() {
  return (
    <main>
      <h1>Regulatory Compliance Agent</h1>
      <p>Frontend is running. Select a section to continue.</p>
      <Link to="/cases">Cases</Link>
    </main>
  );
}

function CasesPage() {
  return (
    <main>
      <h1>Cases</h1>
      <p>Case list view is not implemented yet.</p>
      <Link to="/">Back to dashboard</Link>
    </main>
  );
}

function NotFoundPage() {
  return (
    <main>
      <h1>Page not found</h1>
      <Link to="/">Back to dashboard</Link>
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/cases" element={<CasesPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
