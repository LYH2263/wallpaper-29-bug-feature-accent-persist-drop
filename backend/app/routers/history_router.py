from fastapi import APIRouter
from app.repositories import history as repo

router = APIRouter()


@router.get("/runs")
def list_runs(limit: int = 50, wall_id: int | None = None):
    return {"items": repo.list_runs(limit, wall_id)}
