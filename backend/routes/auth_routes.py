from fastapi import APIRouter, HTTPException, Depends
import pymongo.errors

from models import (
    UserCreate,
    UserLogin,
    UserOut,
    TokenResponse,
    generate_id,
)
from database import users_collection
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    user_id = generate_id()
    user_doc = {
        "_id": user_id,
        "name": payload.name,
        "email": payload.email,
        "password": hash_password(payload.password),
        "role": payload.role,
    }

    try:
        await users_collection.insert_one(user_doc)
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists.",
        )

    return TokenResponse(
        access_token=create_access_token(user_id),
        user=UserOut(id=user_id, name=payload.name, email=payload.email, role=payload.role),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    user = await users_collection.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(
        access_token=create_access_token(user["_id"]),
        user=UserOut(id=user["_id"], name=user["name"], email=user["email"], role=user["role"]),
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user (validates the token)."""
    return UserOut(
        id=current_user["_id"],
        name=current_user["name"],
        email=current_user["email"],
        role=current_user["role"],
    )
