from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def scan_status() -> dict[str, str]:
    return {"message": "Scan endpoints are not implemented yet."}
