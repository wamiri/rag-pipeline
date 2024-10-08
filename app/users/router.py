from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.users import models
from app.users.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.users.schemas import TokenEncode, UserCreate, UserData
from app.users.utils import (
    authenticate_user,
    check_if_user_exists,
    create_access_token,
    create_new_user,
    get_current_active_user,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup")
async def signup(form_data: UserCreate, db: Session = Depends(get_db)):
    user = check_if_user_exists(db, username=form_data.username)
    form_data.password = get_password_hash(form_data.password)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    return create_new_user(db, form_data)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> TokenEncode:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return TokenEncode(access_token=access_token, token_type="bearer")


@router.get("/profile", response_model=UserData)
async def get_profile(
    current_user: Annotated[UserData, Depends(get_current_active_user)],
):
    return current_user
