from http import HTTPStatus

from fastzero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={'username': 'test', 'email': 'test@test.com', 'password': '123'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'test',
        'email': 'test@test.com',
        'id': 1,
    }


def test_create_user_with_same_username(client):
    response = client.post(
        '/users/',
        json={'username': 'test', 'email': 'test@test.com', 'password': '123'},
    )

    assert response.status_code == HTTPStatus.CREATED

    response1 = client.post(
        '/users/',
        json={'username': 'test', 'email': 'test@test.com', 'password': '123'},
    )

    assert response1.status_code == HTTPStatus.CONFLICT
    assert response1.json() == {'detail': 'Username already exists'}


def test_create_user_with_same_email(client):
    response = client.post(
        '/users/',
        json={'username': 'test', 'email': 'test@test.com', 'password': '123'},
    )

    assert response.status_code == HTTPStatus.CREATED

    response1 = client.post(
        '/users/',
        json={
            'username': 'test1',
            'email': 'test@test.com',
            'password': '123',
        },
    )

    assert response1.status_code == HTTPStatus.CONFLICT
    assert response1.json() == {'detail': 'Email already exists'}


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Chopper',
            'email': 'chopper@starwars.com',
            'password': 'rebels',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Chopper',
        'email': 'chopper@starwars.com',
        'id': user.id,
    }


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'new_test',
            'email': 'new_test@test.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
