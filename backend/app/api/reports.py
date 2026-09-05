from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def report_status() -> dict[str, str]:
    return {"message": "Report endpoints are not implemented yet."}
