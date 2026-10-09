from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

# from agents import app  # LangGraph compiled app
from graph import app as compliance_workflow
from app.storage import load_case_state, save_case_state  # you implement these

router = APIRouter(prefix="/hitl", tags=["HITL"])


class HITLApprove(BaseModel):
    case_id: str


class HITLReject(BaseModel):
    case_id: str
    comment: str


class HITLOverride(BaseModel):
    case_id: str
    override_violations: list
    override_score: float
    override_final_response: str
    comment: str


def ensure_case_state(case_id: str) -> Dict[str, Any]:
    state = load_case_state(case_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return state


@router.post("/approve")
def approve_case(payload: HITLApprove):
    state = ensure_case_state(payload.case_id)
    state["hitl_action"] = "approve"

    result = compliance_workflow.invoke(state)
    save_case_state(payload.case_id, result)

    return result


@router.post("/reject")
def reject_case(payload: HITLReject):
    state = ensure_case_state(payload.case_id)
    state["hitl_action"] = "reject"
    state["hitl_comment"] = payload.comment

    result = compliance_workflow.invoke(state)
    save_case_state(payload.case_id, result)

    return result


@router.post("/override")
def override_case(payload: HITLOverride):
    state = ensure_case_state(payload.case_id)
    state["hitl_action"] = "override"
    state["override_violations"] = payload.override_violations
    state["override_score"] = payload.override_score
    state["override_final_response"] = payload.override_final_response
    state["hitl_comment"] = payload.comment

    result = compliance_workflow.invoke(state)
    save_case_state(payload.case_id, result)

    return result
