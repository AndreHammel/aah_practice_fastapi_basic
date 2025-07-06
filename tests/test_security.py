from http import HTTPStatus

from jwt import decode

from fastapi_zero.security import create_access_token


def test_jwt(settings):
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(
        token, settings.SECRET_KEY, algorithms=settings.ALGORITHMS
    )
    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token
