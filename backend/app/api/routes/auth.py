from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.integrations.supabase_client import supabase
from app.core.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    try:
        res = supabase.auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {"data": {"full_name": body.full_name}},
        })
        if res.user is None:
            raise HTTPException(status_code=400, detail="Registration failed")
        return {"message": "Registration successful. Check your email to confirm."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(body: LoginRequest):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
        if res.user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(
            data={"sub": res.user.id, "email": res.user.email}
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": res.user.id, "email": res.user.email},
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout():
    supabase.auth.sign_out()
    return {"message": "Logged out"}
