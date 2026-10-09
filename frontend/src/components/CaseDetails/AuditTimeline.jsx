import React from "react";

export function AuditTimeline({ entries }) {
  if (!entries || entries.length === 0) return null;

  return (
    <div>
      <h2>Audit Log</h2>
      <ul>
        {entries.map((e, idx) => (
          <li key={idx}>
            <strong>{e.timestamp}</strong> — {e.actor} — {e.action}
            {e.details && <pre>{JSON.stringify(e.details, null, 2)}</pre>}
          </li>
        ))}
      </ul>
    </div>
  );
}
