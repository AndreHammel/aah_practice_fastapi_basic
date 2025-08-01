from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import Token
from fastapi_zero.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post(
    '/token', summary='Login para obter token de acesso', response_model=Token
)
async def login_for_access_token(
    session: SessionDep,
    form_data: OAuth2FormDep,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    access_token = create_access_token({
        'sub': user.email,
    })
    return {'access_token': access_token, 'token_type': 'Bearer'}
