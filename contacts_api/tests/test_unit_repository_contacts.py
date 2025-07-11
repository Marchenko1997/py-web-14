import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate
from src.repository.contacts import (
    create_contact,
    get_contacts,
    get_contact_by_id,
    update_contact,
    delete_contact,
    search_contacts,
    upcoming_birthdays,
)

from datetime import date, timedelta


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_create_contact(self):
        contact_data = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="123456789",
            birthday=date(1990, 1, 1),
            additional_info="Test info",
        )
        result = create_contact(self.session, contact_data, self.user)
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.first_name, contact_data.first_name)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = get_contacts(self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = get_contact_by_id(self.session, 1, self.user)
        self.assertEqual(result, contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.query().filter().first.return_value = None
        result = get_contact_by_id(self.session, 1, self.user)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        contact_data = ContactUpdate(
            first_name="Updated",
            last_name="Name",
            email="new@example.com",
            phone="987654321",
            birthday=date(1991, 2, 2),
            additional_info="Updated info",
        )
        result = update_contact(self.session, 1, contact_data, self.user)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        contact_data = ContactUpdate(
            first_name="Updated",
            last_name="Name",
            email="new@example.com",
            phone="987654321",
            birthday=date(1991, 2, 2),
            additional_info="Updated info",
        )
        result = update_contact(self.session, 1, contact_data, self.user)
        self.assertIsNone(result)

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = delete_contact(self.session, 1, self.user)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = delete_contact(self.session, 1, self.user)
        self.assertIsNone(result)

    async def test_search_contacts(self):
        contacts = [Contact()]
        self.session.query().filter().filter().all.return_value = contacts
        result = search_contacts("john", self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_upcoming_birthdays(self):
        contacts = [Contact()]
        self.session.query().filter().filter().all.return_value = contacts
        result = upcoming_birthdays(self.session, self.user)
        self.assertEqual(result, contacts)


if __name__ == "__main__":
    unittest.main()
