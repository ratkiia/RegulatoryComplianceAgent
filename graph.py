from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage

from agents import (
    ComplianceState,
    intent_router,
    pas_lookup,
    guardrails_pre_validation,
    retrieve_cancellation_rules,
    retrieve_nonrenewal_rules,
    retrieve_underwriting_rules,
    validate_cancellation,
    validate_nonrenewal,
    validate_underwriting,
    guardrails_post_validation,
    rule_reasoner,
    guardrails_post_reasoning,
    compliance_score,
    hitl_review,
    escalation,
    response
)

graph = StateGraph(ComplianceState)

# -------------------------
# Register nodes
# -------------------------
graph.add_node("intent_router", intent_router)
graph.add_node("pas_lookup", pas_lookup)

graph.add_node("guardrails_pre_validation", guardrails_pre_validation)

graph.add_node("retrieve_cancellation_rules", retrieve_cancellation_rules)
graph.add_node("retrieve_nonrenewal_rules", retrieve_nonrenewal_rules)
graph.add_node("retrieve_underwriting_rules", retrieve_underwriting_rules)

graph.add_node("validate_cancellation", validate_cancellation)
graph.add_node("validate_nonrenewal", validate_nonrenewal)
graph.add_node("validate_underwriting", validate_underwriting)

graph.add_node("guardrails_post_validation", guardrails_post_validation)

graph.add_node("rule_reasoner", rule_reasoner)
graph.add_node("guardrails_post_reasoning", guardrails_post_reasoning)

graph.add_node("compliance_score", compliance_score)
graph.add_node("hitl_review", hitl_review)
graph.add_node("escalation", escalation)
graph.add_node("response", response)

# -------------------------
# Entrypoint
# -------------------------
graph.set_entry_point("intent_router")

# -------------------------
# Edges
# -------------------------

# Intent → PAS
graph.add_edge("intent_router", "pas_lookup")

# PAS → Guardrails
graph.add_edge("pas_lookup", "guardrails_pre_validation")

# Guardrails → Retrieval (parallel)
graph.add_edge("guardrails_pre_validation", "retrieve_cancellation_rules")
graph.add_edge("guardrails_pre_validation", "retrieve_nonrenewal_rules")
graph.add_edge("guardrails_pre_validation", "retrieve_underwriting_rules")

# Retrieval → Validation (parallel)
graph.add_edge("retrieve_cancellation_rules", "validate_cancellation")
graph.add_edge("retrieve_nonrenewal_rules", "validate_nonrenewal")
graph.add_edge("retrieve_underwriting_rules", "validate_underwriting")

# Validation → Guardrails
graph.add_edge("validate_cancellation", "guardrails_post_validation")
graph.add_edge("validate_nonrenewal", "guardrails_post_validation")
graph.add_edge("validate_underwriting", "guardrails_post_validation")

# Guardrails → Reasoner
graph.add_edge("guardrails_post_validation", "rule_reasoner")

# Reasoner → Guardrails
graph.add_edge("rule_reasoner", "guardrails_post_reasoning")

# Guardrails → Scoring
graph.add_edge("guardrails_post_reasoning", "compliance_score")

# -------------------------
# Conditional HITL / Response
# -------------------------
def score_branch(state: ComplianceState) -> str:
    if state["requires_escalation"]:
        return "hitl_review"
    return "response"

graph.add_conditional_edges("compliance_score", score_branch)

# HITL → END
graph.add_edge("hitl_review", END)

# Response → END
graph.add_edge("response", END)

# -------------------------
# Compile
# -------------------------
app = graph.compile()
