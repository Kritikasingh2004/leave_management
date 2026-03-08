from fastapi import APIRouter, HTTPException, Depends

from models import (
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveRequestOut,
    generate_id,
)
from database import leaves_collection
from auth import get_current_user

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post("/apply", response_model=LeaveRequestOut)
async def apply_leave(
    payload: LeaveRequestCreate,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Only employees can apply for leave")

    leave_id = generate_id()
    leave_doc = {
        "_id": leave_id,
        "employee_id": current_user["_id"],
        "employee_name": current_user["name"],
        "type": payload.type,
        "start_date": payload.start_date.isoformat(),
        "end_date": payload.end_date.isoformat(),
        "reason": payload.reason,
        "status": "pending",
    }
    await leaves_collection.insert_one(leave_doc)

    return LeaveRequestOut(
        id=leave_id,
        employee_id=current_user["_id"],
        employee_name=current_user["name"],
        type=payload.type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status="pending",
    )


@router.get("/all", response_model=list[LeaveRequestOut])
async def get_leaves(current_user: dict = Depends(get_current_user)):
    query = {} if current_user["role"] == "employer" else {"employee_id": current_user["_id"]}
    cursor = leaves_collection.find(query)
    leaves = await cursor.to_list(length=1000)

    return [
        LeaveRequestOut(
            id=l["_id"],
            employee_id=l["employee_id"],
            employee_name=l["employee_name"],
            type=l["type"],
            start_date=l["start_date"],
            end_date=l["end_date"],
            reason=l["reason"],
            status=l["status"],
        )
        for l in leaves
    ]


@router.patch("/{leave_id}", response_model=LeaveRequestOut)
async def update_leave_status(
    leave_id: str,
    payload: LeaveRequestUpdate,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "employer":
        raise HTTPException(status_code=403, detail="Only employers can approve/reject leaves")

    leave = await leaves_collection.find_one({"_id": leave_id})
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    await leaves_collection.update_one(
        {"_id": leave_id},
        {"$set": {"status": payload.status}},
    )

    leave["status"] = payload.status
    return LeaveRequestOut(
        id=leave["_id"],
        employee_id=leave["employee_id"],
        employee_name=leave["employee_name"],
        type=leave["type"],
        start_date=leave["start_date"],
        end_date=leave["end_date"],
        reason=leave["reason"],
        status=leave["status"],
    )
