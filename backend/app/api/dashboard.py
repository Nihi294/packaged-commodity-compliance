from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def dashboard_status() -> dict[str, str]:
    return {"message": "Dashboard endpoints are not implemented yet."}
