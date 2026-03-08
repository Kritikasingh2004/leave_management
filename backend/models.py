from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Literal
from datetime import date
import uuid


# ── Helpers ───────────────────────────────────────────────────────────────

def generate_id() -> str:
    return uuid.uuid4().hex[:12]


# ── User schemas ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    role: Literal["employee", "employer"] = "employee"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Literal["employee", "employer"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Leave Request schemas ─────────────────────────────────────────────────

class LeaveRequestCreate(BaseModel):
    type: Literal["sick", "casual", "annual", "other"] = "casual"
    start_date: date
    end_date: date
    reason: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")
        return self


class LeaveRequestUpdate(BaseModel):
    status: Literal["approved", "rejected"]
    admin_note: str = Field(default="", max_length=500)


class LeaveRequestOut(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    type: str
    start_date: date
    end_date: date
    reason: str
    status: Literal["pending", "approved", "rejected"]
    admin_note: str = ""