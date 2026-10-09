from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List

from app.storage import list_cases, load_case_state

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("")
def get_cases() -> List[Dict[str, Any]]:
    return list_cases()


@router.get("/{case_id}")
def get_case(case_id: str) -> Dict[str, Any]:
    state = load_case_state(case_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return state
