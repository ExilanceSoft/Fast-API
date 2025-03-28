# banjos_restaurant\app\api\routes\user.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from typing import List

from app.schemas.user import UserRegister, UserLogin, Token, UserResponse
from app.models.user import UserModel, UserRole
from app.services.user_service import (
    create_user,
    authenticate_user,
    get_user_by_id,
    update_user,
    delete_user,
    bootstrap_admin,
    get_all_users_from_db,
    refresh_access_token
)
from app.core.auth import (
    get_current_user,
    get_current_active_user,
    require_admin,
    require_superadmin,
    create_access_token,
    create_refresh_token,
    create_csrf_token
)
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.utils.email import send_email

router = APIRouter(prefix="", tags=["Users"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserRegister,
    current_user: UserModel = Depends(require_admin)
):
    try:
        user_data = user.dict()
        new_user = await create_user(user_data, current_user)
        
        send_email(
            recipient=new_user.email,
            subject="Welcome to Banjo's Restaurant",
            template_name="registration_email.html",
            context={
                "username": new_user.username,
                "email": new_user.email
            }
        )
        
        return new_user
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login_user(user: UserLogin):
    authenticated_user = await authenticate_user(user.email, user.password)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user.id},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": authenticated_user.id},
        expires_delta=refresh_token_expires
    )
    
    csrf_token = create_csrf_token(authenticated_user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "csrf_token": csrf_token
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    refresh_token = credentials.credentials
    new_tokens = await refresh_access_token(refresh_token)
    return new_tokens

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user)
):
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: UserModel = Depends(get_current_active_user)
):
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: str,
    update_data: dict,
    request: Request,
    current_user: UserModel = Depends(get_current_active_user)
):
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    updated_user = await update_user(user_id, update_data, current_user)
    return updated_user

@router.delete("/{user_id}")
async def delete_user_profile(
    user_id: str,
    current_user: UserModel = Depends(get_current_active_user)
):
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    await delete_user(user_id, current_user)
    return {"message": "User deleted successfully"}

@router.post("/bootstrap", response_model=UserResponse)
async def bootstrap_admin_user(user: UserRegister):
    user_data = user.dict()
    return await bootstrap_admin(user_data)

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    current_user: UserModel = Depends(require_admin)
):
    return await get_all_users_from_db()