from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: SessionDep):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email already exists'
            )
    db_user = User(
        **user.model_dump(exclude={'password'}),
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=UserList,
)
def read_users(
    current_user: UserDep,
    session: SessionDep,
    filter_users: Annotated[FilterPage, Query()],
):
    users = session.scalars(
        select(User).limit(filter_users.limit).offset(filter_users.offset)
    )
    return {'users': users}


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionDep,
    current_user: UserDep,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )

    user_data = user.model_dump(exclude_unset=True)

    if 'password' in user_data:
        user_data['password'] = get_password_hash(user_data['password'])

    for key, value in user_data.items():
        setattr(current_user, key, value)

    try:
        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError:
        session.rollback()  # Importante fazer rollback em caso de erro
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: UserDep,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )
    session.delete(current_user)
    return {'message': 'User deleted'}


# @router.get(
# '/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
# def read_user_by_id(id: int):
#     if id < 1 or id > len(database):
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail='Deu ruim! Não achei'
#         )
#     user = database[id - 1]
#     return user
