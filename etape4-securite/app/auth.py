"""
Authentication and Authorization Module
Supports JWT and API Key authentication with role-based access control
"""
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_DELTA, security_settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class UserRole(str, Enum):
    """User roles for access control"""
    ADMIN = "admin"           # Full access
    USER = "user"             # API access only
    MONITORING = "monitoring" # Read-only logs/stats

class User(BaseModel):
    """User model"""
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenData(BaseModel):
    """JWT token payload"""
    username: str
    role: UserRole
    exp: datetime
    iat: datetime

# Mock user database (in production, use real database)
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@digitalscore.com",
        "hashed_password": pwd_context.hash("admin123"),
        "role": UserRole.ADMIN,
        "is_active": True,
        "created_at": datetime.now()
    },
    "user": {
        "username": "user",
        "email": "user@digitalscore.com", 
        "hashed_password": pwd_context.hash("user123"),
        "role": UserRole.USER,
        "is_active": True,
        "created_at": datetime.now()
    },
    "monitor": {
        "username": "monitor",
        "email": "monitor@digitalscore.com",
        "hashed_password": pwd_context.hash("monitor123"), 
        "role": UserRole.MONITORING,
        "is_active": True,
        "created_at": datetime.now()
    }
}

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username/password"""
    user = USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    if not user["is_active"]:
        return None
    return user

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + JWT_EXPIRATION_DELTA
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        exp: float = payload.get("exp")
        iat: float = payload.get("iat")
        
        if username is None or role is None:
            return None
            
        return TokenData(
            username=username,
            role=UserRole(role),
            exp=datetime.fromtimestamp(exp),
            iat=datetime.fromtimestamp(iat)
        )
    except jwt.PyJWTError:
        return None

def verify_api_key(api_key: str) -> Optional[UserRole]:
    """Verify API key and return role"""
    if api_key == security_settings.master_api_key:
        return UserRole.ADMIN
    elif api_key == security_settings.admin_api_key:
        return UserRole.ADMIN
    return None

def get_current_user_jwt(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> User:
    """Get current user from JWT token"""
    if not credentials:
        raise AuthenticationError("Token manquant")
    
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise AuthenticationError("Token invalide")
    
    user = USERS_DB.get(token_data.username)
    if not user:
        raise AuthenticationError("Utilisateur introuvable")
    
    if not user["is_active"]:
        raise AuthenticationError("Utilisateur désactivé")
    
    # Update last login
    user["last_login"] = datetime.now()
    
    return User(
        username=user["username"],
        email=user["email"],
        role=user["role"],
        is_active=user["is_active"],
        created_at=user["created_at"],
        last_login=user.get("last_login")
    )

def get_current_user_api_key(api_key: str = Security(api_key_header)) -> User:
    """Get current user from API key"""
    if not api_key:
        raise AuthenticationError("API Key manquante")
    
    role = verify_api_key(api_key)
    if not role:
        raise AuthenticationError("API Key invalide")
    
    # Return admin user for valid API keys
    return User(
        username="api_user",
        email="api@digitalscore.com",
        role=role,
        is_active=True,
        created_at=datetime.now(),
        last_login=datetime.now()
    )

def get_current_user(
    jwt_user: User = Depends(get_current_user_jwt),
    api_user: User = Depends(get_current_user_api_key)
) -> User:
    """Get current user from either JWT or API key (fallback)"""
    # Try JWT first, then API key
    if jwt_user:
        return jwt_user
    return api_user

def require_role(required_roles: List[UserRole]):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise AuthorizationError(
                f"Accès refusé. Rôles requis: {[role.value for role in required_roles]}"
            )
        return current_user
    return role_checker

# Role-based dependencies
require_admin = require_role([UserRole.ADMIN])
require_user_or_admin = require_role([UserRole.USER, UserRole.ADMIN])
require_any_role = require_role([UserRole.USER, UserRole.ADMIN, UserRole.MONITORING])

def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for RGPD compliance"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]
