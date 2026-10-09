import React from "react";

export function ReasoningAccordion({ reasoning }) {
  if (!reasoning || reasoning.length === 0) {
    return <p>No reasoning available.</p>;
  }

  return (
    <div>
      <h2>Reasoning</h2>
      {reasoning.map((r, idx) => (
        <details key={idx}>
          <summary>{r.violation || `Violation ${idx + 1}`}</summary>
          <p><strong>Reason:</strong> {r.reason}</p>
          <p><strong>Supporting Text:</strong> {r.supporting_text}</p>
          <p><strong>Correction:</strong> {r.correction}</p>
        </details>
      ))}
    </div>
  );
}
