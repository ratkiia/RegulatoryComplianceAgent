from fastapi import FastAPI
from app.hitl_router import router as hitl_router
from app.case_router import router as case_router

fastapi_app = FastAPI()

fastapi_app.include_router(case_router)
fastapi_app.include_router(hitl_router)
