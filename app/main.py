from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.v1.endpoints import auth, ghibli, user
from app.core.config import settings
from app.core.initial_data import init_db as init_data
from app.core.logging import (
    get_logger,
    log_request_middleware,
    log_response_middleware,
    setup_logging,
)
from app.db.session import engine, init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de vida de la aplicación
    """
    logger.info(f"Initializing application in {settings.ENVIRONMENT} environment...")
    setup_logging()

    # Inicializar la base de datos
    init_db()

    # Crear datos iniciales solo en desarrollo
    if settings.ENVIRONMENT == "development" and settings.CREATE_INITIAL_DATA:
        logger.info("Creating initial data...")
        with Session(engine) as session:
            init_data(session)
    else:
        logger.info("Skipping initial data creation in production environment")

    logger.info("Application started successfully")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logear requests y responses
    """
    request_data = log_request_middleware(request)
    response = await call_next(request)
    log_response_middleware(response, request_data)
    return response


app.include_router(auth.router, prefix=f"{settings.API_V1_STR}", tags=["auth"])
app.include_router(user.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(
    ghibli.router, prefix=f"{settings.API_V1_STR}/ghibli", tags=["ghibli"]
)


@app.get("/health")
async def health_check():
    """
    Endpoint de health check
    """
    logger.info("Health check requested")
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
