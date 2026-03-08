from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from database import users_collection
from routes.auth_routes import router as auth_router
from routes.leave_routes import router as leave_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await users_collection.create_index("email", unique=True)

    yield


app = FastAPI(
    title="Leave Management System",
    version="0.1.0",
    lifespan=lifespan
)


# ── CORS ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────
app.include_router(auth_router)
app.include_router(leave_router)


# ── Health check ─────────────────────────────────
@app.get("/")
def root():
    return {"message": "Leave Management API is running"}