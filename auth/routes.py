from fastapi import APIRouter, Depends, HTTPException, Path
from auth.schemas import UserResponse, UserCreate, UserLogin
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db import get_session
from auth.models import User
from auth.security import hash_password, verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post('/register', response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    exsisting_user_query=select(User).where(User.email==user.email)
    exsisting_user=await session.exec(exsisting_user_query)

    if exsisting_user.first():
        raise HTTPException(400, "email already exsisted")

    new_user=User(email=user.email,hased_password=hash_password(user.password))

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


from fastapi.security import OAuth2PasswordRequestForm
@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.email == form_data.username) 
    result = await session.exec(stmt)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hased_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user":{
            "id": user.id,
            "email": user.email
        }
    }