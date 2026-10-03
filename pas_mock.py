"""
pas_mock.py

A simple mock Policy Administration System (PAS) that simulates:
- Policy storage
- Policy lookup
- Policy updates
- Endorsements
- Cancellations

This allows compliance agent to behave like it is integrated with a real insurance system.
"""

from typing import Dict, Any


# In-memory policy store (simulates a PAS database)
POLICY_DB: Dict[str, Dict[str, Any]] = {
    "CT-123": {
        "policy_number": "CT-123",
        "state": "CT",
        "notice_days": 10,
        "status": "Active",
        "effective_date": "2024-01-01",
        "insured_name": "John Doe",
        "premium": 1200,
        "endorsements": []
    },
    "NY-555": {
        "policy_number": "NY-555",
        "state": "NY",
        "notice_days": 15,
        "status": "Active",
        "effective_date": "2024-02-01",
        "insured_name": "Alice Smith",
        "premium": 1800,
        "endorsements": []
    }
}


def get_policy(policy_number: str) -> Dict[str, Any]:
    """
    Retrieves a policy from the PAS mock database.

    Args:
        policy_number: The policy number to look up.

    Returns:
        A dictionary representing the policy.
    """
    return POLICY_DB.get(policy_number)


def update_policy(policy_number: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates fields on a policy.

    Args:
        policy_number: The policy to update.
        updates: A dictionary of fields to update.

    Returns:
        The updated policy.
    """
    policy = POLICY_DB.get(policy_number)
    if not policy:
        return None

    policy.update(updates)
    return policy


def add_endorsement(policy_number: str, endorsement: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds an endorsement to a policy.

    Args:
        policy_number: The policy to update.
        endorsement: A dictionary describing the endorsement.

    Returns:
        The updated policy.
    """
    policy = POLICY_DB.get(policy_number)
    if not policy:
        return None

    policy["endorsements"].append(endorsement)
    return policy


def cancel_policy(policy_number: str, reason: str) -> Dict[str, Any]:
    """
    Cancels a policy.

    Args:
        policy_number: The policy to cancel.
        reason: Reason for cancellation.

    Returns:
        The updated policy.
    """
    policy = POLICY_DB.get(policy_number)
    if not policy:
        return None

    policy["status"] = "Cancelled"
    policy["cancellation_reason"] = reason
    return policy
