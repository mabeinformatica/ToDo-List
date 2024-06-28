from sqlalchemy import select

from fastzero.models import User


def test_create_user(session):
    user = User(username='jrf', email='jrf@example.com', password='password')

    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'jrf@example.com')
    )

    assert result.username == 'jrf'
