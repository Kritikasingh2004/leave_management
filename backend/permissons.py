from fastapi import Depends, HTTPException
from auth import get_current_user


async def require_employee(user=Depends(get_current_user)):
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Employee access required")
    return user


async def require_employer(user=Depends(get_current_user)):
    if user["role"] != "employer":
        raise HTTPException(status_code=403, detail="Employer access required")
    return user