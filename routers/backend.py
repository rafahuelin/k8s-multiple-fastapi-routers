from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/hello")
def backend_hello():
    return {"message": "This is backend API"}
