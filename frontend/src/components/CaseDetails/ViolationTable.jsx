import React from "react";

export function ViolationTable({ violations }) {
  if (!violations || violations.length === 0) {
    return <p>No violations.</p>;
  }

  return (
    <div>
      <h2>Violations</h2>
      <table>
        <thead>
          <tr>
            <th>Rule</th>
            <th>Violation</th>
            <th>Severity</th>
          </tr>
        </thead>
        <tbody>
          {violations.map((v, idx) => (
            <tr key={idx}>
              <td>{v.rule}</td>
              <td>{v.violation}</td>
              <td>{v.severity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
