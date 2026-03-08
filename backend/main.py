import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from database import users_collection
from routes.auth_routes import router as auth_router
from routes.leave_routes import router as leave_router

load_dotenv()

raw_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
frontend_url = raw_url.strip().rstrip("/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"DEBUG: Setting CORS to: '{frontend_url}'")
    await users_collection.create_index("email", unique=True)

    yield


app = FastAPI(
    title="Leave Management System",
    version="0.1.0",
    lifespan=lifespan
)


# ── Validation error handler ────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return the first validation error as a plain detail string."""
    errors = exc.errors()
    if errors:
        first = errors[0]
        field = first.get("loc", [""])[-1]
        msg = first.get("msg", "Validation error")
        detail = f"{field}: {msg}" if field else msg
    else:
        detail = "Validation error"
    return JSONResponse(status_code=422, content={"detail": detail})


# ── CORS ────────────────────────────────────────
allowed_origins = [
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://the-leave-manager.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# ── Routers ─────────────────────────────────────
app.include_router(auth_router)
app.include_router(leave_router)


# ── Health check ─────────────────────────────────
@app.get("/")
def root():
    return {"message": "Leave Management API is running"}