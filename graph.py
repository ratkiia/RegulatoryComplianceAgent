"""
graph.py

Defines the LangGraph workflow:
- Nodes: each agent function
- Edges: how state flows between nodes
- Conditional edges: branching based on compliance_score
"""

from langgraph.graph import StateGraph, END
# from state import ComplianceState

# === Import all agent functions ===
from agents import (
    ComplianceState,
    intent_router,
    pas_lookup,
    retrieve_cancellation_rules,
    retrieve_nonrenewal_rules,
    retrieve_underwriting_rules,
    validate_cancellation,
    validate_nonrenewal,
    validate_underwriting,
    rule_reasoner,
    compliance_score,
    escalation,
    response
)

# ============================================================
# Create graph
# ============================================================
graph = StateGraph(ComplianceState)

# ============================================================
# Register nodes (in correct order)
# ============================================================

# Core workflow
graph.add_node("intent_router", intent_router)
graph.add_node("pas_lookup", pas_lookup)

# Parallel rule retrieval nodes
graph.add_node("retrieve_cancellation_rules", retrieve_cancellation_rules)
graph.add_node("retrieve_nonrenewal_rules", retrieve_nonrenewal_rules)
graph.add_node("retrieve_underwriting_rules", retrieve_underwriting_rules)

# Parallel validation nodes
graph.add_node("validate_cancellation", validate_cancellation)
graph.add_node("validate_nonrenewal", validate_nonrenewal)
graph.add_node("validate_underwriting", validate_underwriting)

# Downstream reasoning + scoring
graph.add_node("rule_reasoner", rule_reasoner)
graph.add_node("compliance_score", compliance_score)
graph.add_node("escalation", escalation)
graph.add_node("response", response)

# ============================================================
# Entrypoint
# ============================================================
graph.set_entry_point("intent_router")

# ============================================================
# Edges (correct order)
# ============================================================

# Step 1 — Intent → PAS lookup
graph.add_edge("intent_router", "pas_lookup")

# Step 2 — PAS lookup → Parallel rule retrieval
graph.add_edge("pas_lookup", "retrieve_cancellation_rules")
graph.add_edge("pas_lookup", "retrieve_nonrenewal_rules")
graph.add_edge("pas_lookup", "retrieve_underwriting_rules")

# Step 3 — Retrieval → Validation (parallel)
graph.add_edge("retrieve_cancellation_rules", "validate_cancellation")
graph.add_edge("retrieve_nonrenewal_rules", "validate_nonrenewal")
graph.add_edge("retrieve_underwriting_rules", "validate_underwriting")

# Step 4 — All validation branches → rule_reasoner
graph.add_edge("validate_cancellation", "rule_reasoner")
graph.add_edge("validate_nonrenewal", "rule_reasoner")
graph.add_edge("validate_underwriting", "rule_reasoner")

# Step 5 — Reasoner → Scoring
graph.add_edge("rule_reasoner", "compliance_score")

# Step 6 — Conditional scoring → escalation or response
def score_branch(state: ComplianceState) -> str:
    return "escalation" if state["requires_escalation"] else "response"

graph.add_conditional_edges("compliance_score", score_branch)

# Step 7 — Escalation → Response → END
graph.add_edge("escalation", "response")
graph.add_edge("response", END)

# ============================================================
# Compile the graph
# ============================================================
app = graph.compile()
