from fastapi import FastAPI
from routers import frontend, backend

app = FastAPI()
app.include_router(frontend.router, prefix="/api-for-frontend")
app.include_router(backend.router, prefix="/api-for-backend")
