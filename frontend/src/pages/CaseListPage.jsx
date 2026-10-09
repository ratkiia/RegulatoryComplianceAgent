import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { caseApi } from "../api/caseApi";
import { PolicySummary } from "../components/CaseDetail/PolicySummary";
import { ViolationTable } from "../components/CaseDetail/ViolationTable";
import { ReasoningAccordion } from "../components/CaseDetail/ReasoningAccordion";
import { GuardrailStatus } from "../components/CaseDetail/GuardrailStatus";
import { HITLDecisionPanel } from "../components/CaseDetail/HITLDecisionPanel";
import { AuditTimeline } from "../components/CaseDetail/AuditTimeline";

export function CaseDetailPage() {
  const { caseId } = useParams();
  const [caseData, setCaseData] = useState(null);

  useEffect(() => {
    caseApi.getCase(caseId).then(setCaseData).catch(console.error);
  }, [caseId]);

  if (!caseData) return <p>Loading...</p>;

  return (
    <div>
      <h1>Case {caseId}</h1>
      <PolicySummary data={caseData.policy_data} />
      <ViolationTable violations={caseData.violations} />
      <ReasoningAccordion reasoning={caseData.reasoning} />
      <GuardrailStatus guardrails={caseData.guardrails} />
      <HITLDecisionPanel caseId={caseId} onUpdate={setCaseData} />
      <AuditTimeline entries={caseData.audit_log} />
    </div>
  );
}
