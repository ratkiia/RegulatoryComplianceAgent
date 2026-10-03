"""
agents.py

Defines:
- ComplianceState: shared state structure for the graph
- Agent functions: each node in the LangGraph workflow

Each function:
- Accepts the current state
- Reads from it without mutating in-place
- Returns ONLY the keys it updates (partial state)
"""

import json
from typing import TypedDict, List, Dict, Any, Annotated
from langchain_core.documents import Document
from langgraph.graph import add_messages
from langchain_openai import ChatOpenAI
from rag_pgvector import get_regulation_retriever
from pas_mock import get_policy

llm = ChatOpenAI(model="gpt-4o-mini")  # lightweight, fast


# ============================================================
# Shared state structure used by LangGraph
# ============================================================
class ComplianceState(TypedDict):
    intent: str
    policy_data: Dict[str, Any]

    # Per-category rule sets
    cancellation_rules: List[Document]
    nonrenewal_rules: List[Document]
    underwriting_rules: List[Document]

    # Violations can be written by multiple parallel nodes
    violations: Annotated[List[Dict[str, Any]], add_messages]

    # Downstream reasoning and scoring
    reasoning: List[Dict[str, Any]]
    violation_scores: List[Dict[str, Any]]
    compliance_score: float
    requires_escalation: bool
    final_response: str


# ============================================================
# Intent router
# ============================================================
def intent_router(state: ComplianceState) -> Dict[str, Any]:
    """
    First node in the graph.

    Purpose:
        Ensure that the 'intent' field is set so downstream nodes know what type of compliance check to perform.

    Behavior:
        If 'intent' is missing, default to 'cancellation_compliance'.
    """
    if not state.get("intent"):
        return {"intent": "cancellation_compliance"}
    return {}


# ============================================================
# PAS lookup
# ============================================================
def pas_lookup(state: ComplianceState) -> Dict[str, Any]:
    """
    Retrieves policy data from the PAS mock system. This replaces manually passing policy_data into the graph.
    """
    policy_number = state["policy_data"].get("policy_number")

    policy = get_policy(policy_number)
    if not policy:
        raise ValueError(f"Policy {policy_number} not found in PAS.")

    return {"policy_data": policy}


# ============================================================
# Rule retrieval (per category, parallel-safe)
# ============================================================
def retrieve_cancellation_rules(state: ComplianceState) -> Dict[str, Any]:
    policy = state["policy_data"]
    state_code = policy.get("state")

    retriever = get_regulation_retriever(state_code)
    query = f"{state_code} cancellation notice period requirements"
    docs = retriever.invoke(query)

    return {"cancellation_rules": docs}


def retrieve_nonrenewal_rules(state: ComplianceState) -> Dict[str, Any]:
    policy = state["policy_data"]
    state_code = policy.get("state")

    retriever = get_regulation_retriever(state_code)
    query = f"{state_code} non-renewal notice requirements"
    docs = retriever.invoke(query)

    return {"nonrenewal_rules": docs}


def retrieve_underwriting_rules(state: ComplianceState) -> Dict[str, Any]:
    policy = state["policy_data"]
    state_code = policy.get("state")

    retriever = get_regulation_retriever(state_code)
    query = f"{state_code} underwriting eligibility requirements"
    docs = retriever.invoke(query)

    return {"underwriting_rules": docs}


# ============================================================
# Validation (per category, parallel-safe via multi-write violations)
# ============================================================
def validate_cancellation(state: ComplianceState) -> Dict[str, Any]:
    policy = state["policy_data"]
    rules = state.get("cancellation_rules", [])

    violations = interpret_rules(policy, rules)
    return {"violations": violations}


def validate_nonrenewal(state: ComplianceState) -> Dict[str, Any]:
    policy = state["policy_data"]
    rules = state.get("nonrenewal_rules", [])

    violations = interpret_rules(policy, rules)
    return {"violations": violations}


def validate_underwriting(state: ComplianceState) -> Dict[str, Any]:
    policy = state["policy_data"]
    rules = state.get("underwriting_rules", [])

    violations = interpret_rules(policy, rules)
    return {"violations": violations}


# ============================================================
# Rule reasoner
# ============================================================
def rule_reasoner(state: ComplianceState) -> Dict[str, Any]:
    """
    Provide deeper reasoning for each detected violation using an LLM.
    """

    violations = state.get("violations", [])
    policy = state.get("policy_data", {})

    # Combine all rule text into one block from all categories
    all_rules: List[Document] = []
    all_rules.extend(state.get("cancellation_rules", []))
    all_rules.extend(state.get("nonrenewal_rules", []))
    all_rules.extend(state.get("underwriting_rules", []))

    if not violations:
        return {"reasoning": []}

    rule_text = "\n\n".join([doc.page_content for doc in all_rules])

    prompt = f"""
    You are a regulatory compliance analyst.

    Policy data:
    {policy}

    Regulatory rules:
    {rule_text}

    Violations detected:
    {violations}

    Task:
    For each violation:
    - Explain WHY the violation applies.
    - Quote the specific regulatory text that supports the violation.
    - Provide guidance on how the policy could be corrected.
    - Return output as a JSON list of objects:
      [{{"violation": "...", "reason": "...", "supporting_text": "...", "correction": "..."}}]
    """

    response = llm.invoke(prompt)

    try:
        reasoning = json.loads(response.content)
    except Exception:
        reasoning = [{"raw": response.content}]

    return {"reasoning": reasoning}


# ============================================================
# Compliance scoring
# ============================================================
def compliance_score(state: ComplianceState) -> Dict[str, Any]:
    """
    Convert violations into a numeric compliance score and decide whether escalation is required.
    """

    violations = state.get("violations", [])

    # No violations → perfect score
    if not violations:
        return {
            "violation_scores": [],
            "compliance_score": 100.0,
            "requires_escalation": False,
        }

    violation_scores = score_violations(violations)
    total_deduction = sum(v["score"] for v in violation_scores)
    final_score = max(0, 100 - total_deduction)

    return {
        "violation_scores": violation_scores,
        "compliance_score": final_score,
        "requires_escalation": final_score < 70,
    }


# ============================================================
# Escalation and response
# ============================================================
def escalation(state: ComplianceState) -> Dict[str, Any]:
    """
    Handle non-compliant cases that require human review.
    """
    return {"final_response": "Non-compliant. Escalate to underwriter."}


def response(state: ComplianceState) -> Dict[str, Any]:
    """
    Produce a user-facing summary of the compliance result.
    """
    if state.get("requires_escalation"):
        return {}
    return {"final_response": "Compliant. No escalation required."}


# ============================================================
# Helper: interpret rules into violations
# ============================================================
def interpret_rules(policy: Dict[str, Any], rules: List[Document]) -> List[Dict[str, Any]]:
    if not rules:
        return []

    rule_text = "\n\n".join([doc.page_content for doc in rules])

    prompt = f"""
    You are a regulatory compliance expert.

    Policy data:
    {policy}

    Regulatory rules:
    {rule_text}

    Task:
    - Identify any compliance violations.
    - Explain each violation clearly.
    - Include severity: low, medium, high.
    - Return output as a JSON list of objects:
      [{{"rule": "...", "violation": "...", "severity": "..."}}]
    """

    response = llm.invoke(prompt)

    try:
        parsed = json.loads(response.content)
        if isinstance(parsed, list):
            return parsed
        else:
            return [{
                "rule": "LLM returned non-list",
                "violation": response.content,
                "severity": "medium",
            }]
    except Exception:
        return [{
            "rule": "LLM JSON parsing error",
            "violation": response.content,
            "severity": "medium",
        }]


# ============================================================
# Helper: score violations
# ============================================================
def score_violations(violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    severity_weights = {
        "high": 50,
        "medium": 30,
        "low": 10,
    }

    scored: List[Dict[str, Any]] = []

    for v in violations:
        severity = v.get("severity", "medium").lower()
        deduction = severity_weights.get(severity, 30)
        scored.append({
            "severity": severity,
            "score": deduction,
        })

    return scored
