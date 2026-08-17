from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apps.api.routers import auth, samples, sandbox, telemetry, metrics

app = FastAPI(
    title="RansomShield AI Core API",
    description="Secure Active Ransomware Behaviour Analysis Sandbox API",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(samples.router, prefix="/api/v1/samples", tags=["samples"])
app.include_router(sandbox.router, prefix="/api/v1/sandbox", tags=["sandbox"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["telemetry"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to RansomShield AI - API is running. LAB ISOLATION REQUIRED."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Future endpoints will be registered here (samples, telemetry, analyses, etc.)

