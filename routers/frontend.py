from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/hello")
def frontend_hello():
    return {"message": "This is frontend API"}
