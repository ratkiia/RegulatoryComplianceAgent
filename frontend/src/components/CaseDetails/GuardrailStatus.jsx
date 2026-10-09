import React from "react";

export function GuardrailStatus({ guardrails }) {
  if (!guardrails) return null;

  return (
    <div>
      <h2>Guardrails</h2>
      <p>Pre-validation: {guardrails.pre_validation}</p>
      <p>Post-validation: {guardrails.post_validation}</p>
      <p>Post-reasoning: {guardrails.post_reasoning}</p>
    </div>
  );
}
