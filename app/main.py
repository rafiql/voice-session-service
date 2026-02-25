from fastapi import FastAPI
from app.api.session_routes import router as session_router

app = FastAPI(
    title="Voice Session Service",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(session_router)