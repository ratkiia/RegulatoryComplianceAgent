from datetime import datetime
from typing import Dict, Any, List, Optional
"""
storage.py

In-memory storage for HITL cases + placeholder for PostgreSQL.

This module provides:
- create_case_state(case_id, initial_state)
- load_case_state(case_id)
- save_case_state(case_id, state)
- list_cases()
- append_audit_log(case_id, entry)

Later you can replace the in-memory dict with PostgreSQL.
"""

# ============================================================
# In-memory storage (development mode)
# ============================================================

# Stores full LangGraph state for each case


_CASES: Dict[str, Dict[str, Any]] = {}

# Stores audit logs per case
_AUDIT_LOGS: Dict[str, List[Dict[str, Any]]] = {}


# ============================================================
# Case Management
# ============================================================

def create_case_state(case_id: str, initial_state: Dict[str, Any]) -> None:
    """
    Create a new case in memory.
    """
    initial_state["id"] = case_id
    initial_state["created_at"] = datetime.utcnow().isoformat()
    initial_state["updated_at"] = datetime.utcnow().isoformat()
    initial_state.setdefault("audit_log", [])

    _CASES[case_id] = initial_state
    _AUDIT_LOGS[case_id] = []


def load_case_state(case_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a case state from memory.
    """
    return _CASES.get(case_id)


def save_case_state(case_id: str, state: Dict[str, Any]) -> None:
    """
    Save updated case state.
    """
    state["updated_at"] = datetime.utcnow().isoformat()
    _CASES[case_id] = state


def list_cases() -> List[Dict[str, Any]]:
    """
    Return all cases.
    """
    return list(_CASES.values())


# ============================================================
# Audit Logging
# ============================================================

def append_audit_log(case_id: str, actor: str, action: str, details: Dict[str, Any]) -> None:
    """
    Append an audit log entry for a case.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "actor": actor,
        "action": action,
        "details": details,
    }

    _AUDIT_LOGS[case_id].append(entry)

    # Also store inside case state for UI
    if "audit_log" not in _CASES[case_id]:
        _CASES[case_id]["audit_log"] = []

    _CASES[case_id]["audit_log"].append(entry)


def get_audit_log(case_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve audit log entries for a case.
    """
    return _AUDIT_LOGS.get(case_id, [])


# ============================================================
# PostgreSQL Placeholder
# ============================================================


# End of storage.py
