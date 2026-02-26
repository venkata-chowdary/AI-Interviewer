from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.auth.models import User
from app.auth.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    stmt = select(User).where(User.id == UUID(user_id))
    result = await session.exec(stmt)
    user = result.first()

    if not user:
        raise HTTPException(401, "User not found")
    return user
