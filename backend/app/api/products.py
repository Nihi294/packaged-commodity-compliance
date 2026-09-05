from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def product_status() -> dict[str, str]:
    return {"message": "Product endpoints are not implemented yet."}
