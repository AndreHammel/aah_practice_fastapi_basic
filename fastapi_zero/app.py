from http import HTTPStatus
from fastapi import FastAPI
from fastapi_zero.schemas import Message

app = FastAPI(title='API Pratica')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}
