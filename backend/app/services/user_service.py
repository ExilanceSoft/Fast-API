# banjos_restaurant\app\services\user_service.py
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from app.core.database import dynamodb
from app.models.user import UserModel, UserRole, UserCreate, UserUpdate
from app.core.auth import create_access_token, create_refresh_token, create_csrf_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def create_user(user_data: Dict[str, Any], current_user: UserModel) -> UserModel:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create users"
        )

    try:
        # Check if email or mobile number already exists
        items = await dynamodb.scan()
        for item in items:
            if item.get("Home", {}).get("S") == "Users":
                if item.get("email", {}).get("S") == user_data["email"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                if item.get("mobile_number", {}).get("S") == user_data["mobile_number"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Mobile number already registered"
                    )

        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_data["password"])

        item = {
            "Home": {"S": "Users"},
            "1": {"S": user_id},
            "username": {"S": user_data["username"]},
            "email": {"S": user_data["email"]},
            "mobile_number": {"S": user_data["mobile_number"]},
            "password": {"S": hashed_password},
            "role": {"S": user_data["role"]},
            "disabled": {"BOOL": False},
            "created_at": {"S": datetime.utcnow().isoformat()},
            "updated_at": {"S": datetime.utcnow().isoformat()}
        }

        await dynamodb.put_item(item)
        
        return UserModel(
            id=user_id,
            username=user_data["username"],
            email=user_data["email"],
            mobile_number=user_data["mobile_number"],
            role=user_data["role"],
            disabled=False
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

async def authenticate_user(email: str, password: str) -> Optional[UserModel]:
    try:
        items = await dynamodb.scan()
        for item in items:
            if item.get("Home", {}).get("S") == "Users":
                if item.get("email", {}).get("S") == email:
                    user_data = {
                        "id": item.get("1", {}).get("S", ""),
                        "username": item.get("username", {}).get("S", ""),
                        "email": item.get("email", {}).get("S", ""),
                        "mobile_number": item.get("mobile_number", {}).get("S", ""),
                        "password": item.get("password", {}).get("S", ""),
                        "role": item.get("role", {}).get("S", ""),
                        "disabled": item.get("disabled", {}).get("BOOL", False)
                    }
                    if verify_password(password, user_data["password"]):
                        return UserModel(**user_data)
                    break
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

async def get_user_by_id(user_id: str) -> Optional[UserModel]:
    try:
        key = {
            "Home": {"S": "Users"},
            "1": {"S": user_id}
        }
        item = await dynamodb.get_item(key)
        if not item:
            return None
        
        return UserModel(
            id=item.get("1", {}).get("S", ""),
            username=item.get("username", {}).get("S", ""),
            email=item.get("email", {}).get("S", ""),
            mobile_number=item.get("mobile_number", {}).get("S", ""),
            role=item.get("role", {}).get("S", ""),
            disabled=item.get("disabled", {}).get("BOOL", False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}"
        )

async def update_user(
    user_id: str,
    update_data: Dict[str, Any],
    current_user: UserModel
) -> UserModel:
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    try:
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        if "username" in update_data:
            update_expression += "#un = :un, "
            expression_attribute_names["#un"] = "username"
            expression_attribute_values[":un"] = {"S": update_data["username"]}

        if "email" in update_data:
            # Check if new email is already taken
            items = await dynamodb.scan()
            for item in items:
                if item.get("Home", {}).get("S") == "Users":
                    if item.get("email", {}).get("S") == update_data["email"] and item.get("1", {}).get("S") != user_id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already in use by another user"
                        )
            update_expression += "email = :em, "
            expression_attribute_values[":em"] = {"S": update_data["email"]}

        if "mobile_number" in update_data:
            # Check if new mobile number is already taken
            items = await dynamodb.scan()
            for item in items:
                if item.get("Home", {}).get("S") == "Users":
                    if item.get("mobile_number", {}).get("S") == update_data["mobile_number"] and item.get("1", {}).get("S") != user_id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Mobile number already in use by another user"
                        )
            update_expression += "mobile_number = :mn, "
            expression_attribute_values[":mn"] = {"S": update_data["mobile_number"]}

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            update_expression += "password = :pw, "
            expression_attribute_values[":pw"] = {"S": hashed_password}

        update_expression += "updated_at = :ua"
        expression_attribute_values[":ua"] = {"S": datetime.utcnow().isoformat()}

        key = {
            "Home": {"S": "Users"},
            "1": {"S": user_id}
        }

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values
        )

        return await get_user_by_id(user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

async def delete_user(user_id: str, current_user: UserModel) -> bool:
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )

    try:
        key = {
            "Home": {"S": "Users"},
            "1": {"S": user_id}
        }
        item = await dynamodb.get_item(key)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        await dynamodb.delete_item(key)
        return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )

async def is_database_empty() -> bool:
    try:
        items = await dynamodb.scan()
        for item in items:
            if item.get("Home", {}).get("S") == "Users":
                return False
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking database: {str(e)}"
        )

async def bootstrap_admin(user_data: Dict[str, Any]) -> UserModel:
    if not await is_database_empty():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap is only allowed when no users exist"
        )

    try:
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_data["password"])

        item = {
            "Home": {"S": "Users"},
            "1": {"S": user_id},
            "username": {"S": user_data["username"]},
            "email": {"S": user_data["email"]},
            "mobile_number": {"S": user_data["mobile_number"]},
            "password": {"S": hashed_password},
            "role": {"S": UserRole.SUPERADMIN},
            "disabled": {"BOOL": False},
            "created_at": {"S": datetime.utcnow().isoformat()},
            "updated_at": {"S": datetime.utcnow().isoformat()}
        }

        await dynamodb.put_item(item)
        
        return UserModel(
            id=user_id,
            username=user_data["username"],
            email=user_data["email"],
            mobile_number=user_data["mobile_number"],
            role=UserRole.SUPERADMIN,
            disabled=False
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error bootstrapping admin: {str(e)}"
        )

async def get_all_users_from_db() -> List[UserModel]:
    try:
        items = await dynamodb.scan()
        users = []
        
        for item in items:
            if item.get("Home", {}).get("S") == "Users":
                users.append(UserModel(
                    id=item.get("1", {}).get("S", ""),
                    username=item.get("username", {}).get("S", ""),
                    email=item.get("email", {}).get("S", ""),
                    mobile_number=item.get("mobile_number", {}).get("S", ""),
                    role=item.get("role", {}).get("S", ""),
                    disabled=item.get("disabled", {}).get("BOOL", False)
                ))
        
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )

async def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        new_csrf_token = create_csrf_token(user.id)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "csrf_token": new_csrf_token
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )