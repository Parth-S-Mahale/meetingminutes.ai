from fastapi import FastAPI

from app.api.meetings import router as meetings_router
from app.config import get_settings
from app.database import Base, engine
from app.services.file_service import ensure_directories

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


@app.on_event("startup")
def on_startup():
    """
    Create DB tables and required local directories on app startup.
    """
    Base.metadata.create_all(bind=engine)
    ensure_directories()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(meetings_router, prefix=settings.API_V1_PREFIX)