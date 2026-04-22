"""
SLIS — FastAPI Backend Entry Point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.ml_service import ml_service
from backend.data_store import data_store
from backend.routes import students, predict, dashboard, recommendations, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[SLIS] Starting up...")
    data_store.load()
    ml_service.load()
    print("[SLIS] Ready!")
    yield
    # Shutdown
    print("[SLIS] Shutting down.")


app = FastAPI(
    title="SLIS — Student Learning Intelligence System",
    version="1.0.0",
    description="AI-powered student performance analytics and risk prediction API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(recommendations.router)
app.include_router(upload.router)


@app.get("/")
def root():
    return {"message": "SLIS API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": ml_service.classifier is not None}
