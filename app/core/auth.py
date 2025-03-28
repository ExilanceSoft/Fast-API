# banjos_restaurant\app\core\auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECURE_COOKIES,
    CSRF_PROTECTION
)
from app.models.user import UserModel, UserRole
from app.core.database import dynamodb

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
security = HTTPBearer()

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
        # CSRF protection for state-changing requests
        if CSRF_PROTECTION and request and request.method not in ["GET", "HEAD", "OPTIONS"]:
            csrf_token = request.headers.get("X-CSRF-Token")
            if not csrf_token or not verify_csrf_token(csrf_token, user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token validation failed"
                )
    except JWTError:
        raise credentials_exception
    
    user = await get_user_from_db(user_id)
    if not user:
        raise credentials_exception
    
    return user

async def get_user_from_db(user_id: str) -> Optional[UserModel]:
    key = {
        "Home": {"S": "Users"},
        "1": {"S": user_id}
    }
    user = await dynamodb.get_item(key)
    if not user:
        return None
    
    return UserModel(
        id=user.get("1", {}).get("S", ""),
        username=user.get("username", {}).get("S", ""),
        email=user.get("email", {}).get("S", ""),
        mobile_number=user.get("mobile_number", {}).get("S", ""),
        role=user.get("role", {}).get("S", ""),
        password="",  # Password should not be returned
        disabled=user.get("disabled", {}).get("BOOL", False)
    )

def verify_csrf_token(token: str, user_id: str) -> bool:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("sub") == user_id and payload.get("type") == "csrf"
    except JWTError:
        return False

def create_csrf_token(user_id: str) -> str:
    data = {"sub": user_id, "type": "csrf"}
    return jwt.encode(data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def require_admin(current_user: UserModel = Depends(get_current_active_user)) -> UserModel:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def require_superadmin(current_user: UserModel = Depends(get_current_active_user)) -> UserModel:
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin privileges required"
        )
    return current_user