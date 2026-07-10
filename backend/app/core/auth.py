
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AppException
from app.core.jwt import verify_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppException(401, "UNAUTHORIZED", "Authentication required")

    user_id = verify_access_token(credentials.credentials)
    if not user_id:
        raise AppException(401, "TOKEN_EXPIRED", "Invalid or expired access token")

    user = await UserRepository.get_by_id(user_id)
    if not user or not user.is_active:
        raise AppException(401, "UNAUTHORIZED", "User account is inactive")

    return user
