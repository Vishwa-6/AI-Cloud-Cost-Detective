from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from auth.database import engine, Base
from scan.routes import router as scan_router
import scan.models  # register Analysis table

# Create database tables
Base.metadata.create_all(bind=engine)

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Validate critical environment variables
if not os.environ.get("GEMINI_API_KEY"):
    sys.exit("\n❌ CRITICAL ERROR: GEMINI_API_KEY is missing in your .env file.\n"
             "Please add it before starting the backend server.\n")

from limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI()

# Register Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Restrict CORS to specific frontend origin for better security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(scan_router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "FinOps Sentinel Backend"}
