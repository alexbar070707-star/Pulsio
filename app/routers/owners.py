from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.rate_limit import rate_limit
from app.models.owner import Owner
import uuid

router = APIRouter(prefix="/owners", tags=["owners"])

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=201)
async def register(req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    rate_limit(request, "register")
    # Check existing
    result = await db.execute(select(Owner).where(Owner.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    owner = Owner(
        id=str(uuid.uuid4()),
        email=req.email,
        username=req.username,
        hashed_password=hash_password(req.password),
    )
    db.add(owner)
    await db.commit()
    await db.refresh(owner)
    return {"id": owner.id, "username": owner.username, "message": "Welcome to Pulsio"}

@router.post("/login")
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    rate_limit(request, "login")
    result = await db.execute(select(Owner).where(Owner.email == req.email))
    owner = result.scalar_one_or_none()
    if not owner or not verify_password(req.password, owner.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not owner.is_active:
        raise HTTPException(status_code=403, detail="Account suspended")

    token = create_access_token({"sub": owner.id, "type": "owner"})
    return {"access_token": token, "token_type": "bearer", "username": owner.username}
