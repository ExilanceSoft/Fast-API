# banjos_restaurant\app\core\config.py
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# DynamoDB configuration
AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
DYNAMODB_TABLE: str = os.getenv("DYNAMODB_TABLE", "banjosthefoodchain")

# JWT configuration
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-very-secret-key-123456")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Security
SECURE_COOKIES: bool = os.getenv("SECURE_COOKIES", "True") == "True"
CSRF_PROTECTION: bool = os.getenv("CSRF_PROTECTION", "True") == "True"

# Static files configuration
STATIC_FILES_DIR: str = "static"
IMAGES_DIR: str = os.path.join(STATIC_FILES_DIR, "images")

# Ensure the static/images directory exists
os.makedirs(IMAGES_DIR, exist_ok=True)