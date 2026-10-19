from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import auth, categories, inventory, products, reports, suppliers, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para sistema de gestión de inventarios",
    lifespan=lifespan,
)

logger = logging.getLogger(__name__)


# Convierte excepciones no controladas en 500 *dentro* de CORSMiddleware; si no,
# las genera ServerErrorMiddleware (más externo) y salen sin cabeceras CORS.
@app.middleware("http")
async def catch_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Error no controlado en %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# CORS se añade al final para que sea el middleware más externo (Starlette
# envuelve en orden inverso) y todas las respuestas (401/404/500) lleven cabeceras.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "message": "Sistema de Gestión de Inventarios",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
