import React from "react";

export function PolicySummary({ data }) {
  if (!data) return null;

  return (
    <div>
      <h2>Policy Summary</h2>
      <p>Policy #: {data.policy_number}</p>
      <p>State: {data.state}</p>
      <p>Notice Days: {data.notice_days}</p>
      <p>Effective Date: {data.effective_date}</p>
      <p>Insured: {data.insured_name}</p>
      <p>Product: {data.product_type}</p>
    </div>
  );
}
