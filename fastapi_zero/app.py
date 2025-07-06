from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI(title='API Pratica')

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
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


@app.get(
    '/users/',
    status_code=HTTPStatus.OK,
    response_model=UserList,
)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # user_db = session.scalar(select(User).where(User.id == user_id))
    # if not user_db:
    #     raise HTTPException(
    #         status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    #     )

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


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )

    # user_db = session.scalar(select(User).where(User.id == user_id))
    # if not user_db:
    #     raise HTTPException(
    #         status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    #     )
    session.delete(current_user)
    return {'message': 'User deleted'}


@app.get('/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user_by_id(id: int):
    if id < 1 or id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Deu ruim! Não achei'
        )
    user = database[id - 1]
    return user


@app.post(
    '/token', summary='Login para obter token de acesso', response_model=Token
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))
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
