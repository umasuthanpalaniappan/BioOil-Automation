import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.model_registry import registry
from app.routers import batch, drift, explain, export, models, predict

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("pyrolysis.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.load()
    if registry.loaded:
        logger.info("Model registry loaded: %d O/C models, %d secondary models",
                     len(registry.oc_models), len(registry.secondary_models))
    else:
        logger.warning("Model registry NOT loaded — run the training pipeline first "
                        "(ml/src/train.py) and ensure MODELS_DIR points at ml/models")
    yield


app = FastAPI(
    title="Bio-Oil Pyrolysis Deoxygenation API",
    description="Predicts and helps optimize pyrolysis conditions to minimize "
                 "bio-oil oxygen content (O/C ratio).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info("%s %s -> %d (%.1fms)", request.method, request.url.path,
                response.status_code, duration_ms)
    return response


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": registry.loaded,
            "available_models": registry.available_models()}


app.include_router(predict.router)
app.include_router(batch.router)
app.include_router(models.router)
app.include_router(explain.router)
app.include_router(drift.router)
app.include_router(export.router)
