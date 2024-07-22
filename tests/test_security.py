from http import HTTPStatus

from jwt import decode

from fastzero.security import create_access_token, settings


def test_jwt():
    payload = {'sub': 'teste@test.com'}
    token = create_access_token(payload)

    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == payload['sub']
    assert result['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
