from http import HTTPStatus

from fastzero.models import TodoState
from tests.conftest import TodoFactory


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Teste',
            'description': 'Descrição do teste',
            'state': 'draft',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'title': 'Teste',
        'description': 'Descrição do teste',
        'state': 'draft',
    }


def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5

    session.bulk_save_objects(TodoFactory.create_batch(5, userId=user.id))
    session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):
    expected_todos = 2

    session.bulk_save_objects(TodoFactory.create_batch(5, userId=user.id))
    session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_title_should_return_5_todos(
    session, client, user, token
):
    expected_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(5, userId=user.id, title='Teste todo 1')
    )
    session.commit()

    response = client.get(
        '/todos/?title=todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_description_should_return_5_todos(
    session, client, user, token
):
    expected_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(5, userId=user.id, description='Teste todo 1')
    )
    session.commit()

    response = client.get(
        '/todos/?description=todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_state_should_return_5_todos(
    session, client, user, token
):
    expected_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(5, userId=user.id, state=TodoState.draft)
    )
    session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            userId=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            userId=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(userId=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted'}


def test_delete_todo_error(client, token):
    response = client.delete(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_patch_todo(session, client, user, token):
    todo = TodoFactory(userId=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Updated title'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'Updated title'


def test_patch_error(client, token):
    response = client.patch(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}
