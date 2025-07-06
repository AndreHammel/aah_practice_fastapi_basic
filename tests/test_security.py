from http import HTTPStatus

from jwt import decode

from fastapi_zero.security import ALGORITHMS, SECRET_KEY, create_access_token


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHMS)
    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token
