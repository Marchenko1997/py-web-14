import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirm_email,
    update_avatar,
    update_password,
)


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        user = User(email="test@example.com")
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email("test@example.com", self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email("notfound@example.com", self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(email="new@example.com", password="hashedpass")
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh = lambda x: setattr(x, "id", 1)
        result = await create_user(body, self.session)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User()
        await update_token(user, "refresh_token", self.session)
        self.assertEqual(user.refresh_token, "refresh_token")

    async def test_confirm_email_user_found(self):
        user = User(email="test@example.com", confirmed=False)
        self.session.query().filter().first.return_value = user
        result = await confirm_email("test@example.com", self.session)
        self.assertTrue(result.confirmed)

    async def test_confirm_email_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await confirm_email("notfound@example.com", self.session)
        self.assertIsNone(result)

    async def test_update_avatar(self):
        user = User()
        result = await update_avatar(user, "http://avatar.com/img.png", self.session)
        self.assertEqual(result.avatar, "http://avatar.com/img.png")

    async def test_update_password_user_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        await update_password("test@example.com", "newhashed", self.session)
        self.assertEqual(user.password, "newhashed")

    async def test_update_password_user_not_found(self):
        self.session.query().filter().first.return_value = None
        await update_password("missing@example.com", "newhashed", self.session)
        self.assertIsNone(self.session.refresh.call_args)


if __name__ == "__main__":
    unittest.main()
