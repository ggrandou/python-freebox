"""Unit tests for the Contact (phonebook) API."""
import pytest

from freebox import (
    Contact,
    ContactAddress,
    ContactEmail,
    ContactEntry,
    ContactNumber,
    ContactUrl,
    Freebox,
)
from tests.conftest import (
    APP_ID,
    APP_NAME,
    APP_VERSION,
    DEVICE_NAME,
    DISCOVERY_DATA,
    SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def fb(httpx_mock, tmp_path):
    token_file = tmp_path / "token"
    token_file.write_text("test-app-token")
    httpx_mock.add_response(url=f"{BASE}/api_version", json=DISCOVERY_DATA)
    httpx_mock.add_response(
        url=f"{API}/login/",
        json=api_ok({"logged_in": False, "challenge": "chal"}),
    )
    httpx_mock.add_response(
        url=f"{API}/login/session/",
        method="POST",
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"contacts": True}}),
    )
    client = Freebox(
        app_id=APP_ID,
        app_name=APP_NAME,
        app_version=APP_VERSION,
        device_name=DEVICE_NAME,
        token_file=token_file,
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Test data ─────────────────────────────────────────────────────────────────

NUMBER_DICT = {
    "id": 1,
    "contact_id": 10,
    "type": "fixed",
    "number": "0612345678",
    "is_default": True,
    "is_own": False,
}

ADDRESS_DICT = {
    "id": 2,
    "contact_id": 10,
    "type": "home",
    "number": "11",
    "street": "8 rue du pont",
    "street2": "",
    "city": "Paris",
    "zipcode": "75008",
    "country": "France",
}

URL_DICT = {
    "id": 3,
    "contact_id": 10,
    "type": "site",
    "url": "http://www.example.com/",
}

EMAIL_DICT = {
    "id": 4,
    "contact_id": 10,
    "type": "home",
    "email": "mamie@example.org",
}

CONTACT_DICT = {
    "id": 10,
    "display_name": "Mamie Kipic",
    "first_name": "Mamie",
    "last_name": "Kipic",
    "company": "",
    "photo_url": "",
    "last_update": 1363973599,
    "birthday": "",
    "notes": "",
    "numbers": [NUMBER_DICT],
    "addresses": [ADDRESS_DICT],
    "urls": [URL_DICT],
    "emails": [EMAIL_DICT],
}

CONTACT_MINIMAL = {
    "id": 11,
    "display_name": "Sandy Kilo",
    "first_name": "Sandy",
    "last_name": "Kilo",
    "company": "",
    "photo_url": "",
    "last_update": 1372433423,
    "birthday": "",
    "notes": "",
}


# ── ContactNumber ─────────────────────────────────────────────────────────────

def test_contact_number_from_dict():
    n = ContactNumber._from_dict(NUMBER_DICT)
    assert n.id == 1
    assert n.contact_id == 10
    assert n.type == "fixed"
    assert n.number == "0612345678"
    assert n.is_default is True
    assert n.is_own is False


def test_contact_number_defaults():
    n = ContactNumber._from_dict({})
    assert n.id == 0
    assert n.number == ""
    assert n.is_default is False


# ── ContactAddress ────────────────────────────────────────────────────────────

def test_contact_address_from_dict():
    a = ContactAddress._from_dict(ADDRESS_DICT)
    assert a.id == 2
    assert a.city == "Paris"
    assert a.zipcode == "75008"
    assert a.country == "France"
    assert a.street == "8 rue du pont"


def test_contact_address_defaults():
    a = ContactAddress._from_dict({})
    assert a.city == ""
    assert a.street2 == ""


# ── ContactUrl ────────────────────────────────────────────────────────────────

def test_contact_url_from_dict():
    u = ContactUrl._from_dict(URL_DICT)
    assert u.id == 3
    assert u.type == "site"
    assert u.url == "http://www.example.com/"


def test_contact_url_defaults():
    u = ContactUrl._from_dict({})
    assert u.url == ""


# ── ContactEmail ──────────────────────────────────────────────────────────────

def test_contact_email_from_dict():
    e = ContactEmail._from_dict(EMAIL_DICT)
    assert e.id == 4
    assert e.type == "home"
    assert e.email == "mamie@example.org"


def test_contact_email_defaults():
    e = ContactEmail._from_dict({})
    assert e.email == ""


# ── ContactEntry ──────────────────────────────────────────────────────────────

def test_contact_entry_from_dict():
    c = ContactEntry._from_dict(CONTACT_DICT)
    assert c.id == 10
    assert c.display_name == "Mamie Kipic"
    assert c.first_name == "Mamie"
    assert c.last_name == "Kipic"
    assert len(c.numbers) == 1
    assert c.numbers[0].number == "0612345678"
    assert len(c.addresses) == 1
    assert c.addresses[0].city == "Paris"
    assert len(c.urls) == 1
    assert c.urls[0].url == "http://www.example.com/"
    assert len(c.emails) == 1
    assert c.emails[0].email == "mamie@example.org"


def test_contact_entry_minimal():
    c = ContactEntry._from_dict(CONTACT_MINIMAL)
    assert c.id == 11
    assert c.numbers == []
    assert c.addresses == []
    assert c.urls == []
    assert c.emails == []


def test_contact_entry_null_sub_lists():
    d = dict(CONTACT_DICT, numbers=None, addresses=None, urls=None, emails=None)
    c = ContactEntry._from_dict(d)
    assert c.numbers == []
    assert c.addresses == []
    assert c.urls == []
    assert c.emails == []


# ── Contact.list ──────────────────────────────────────────────────────────────

def test_list(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/",
        json=api_ok([CONTACT_DICT, CONTACT_MINIMAL]),
    )
    contacts = fb.contact.list()
    assert len(contacts) == 2
    assert contacts[0].display_name == "Mamie Kipic"
    assert contacts[1].display_name == "Sandy Kilo"


def test_list_empty(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/contact/", json=api_ok([]))
    assert fb.contact.list() == []


def test_list_null(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/contact/", json=api_ok(None))
    assert fb.contact.list() == []


def test_list_with_params(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/?start=10&limit=5&group_id=2",
        json=api_ok([]),
    )
    result = fb.contact.list(start=10, limit=5, group_id=2)
    assert result == []


# ── Contact.get ───────────────────────────────────────────────────────────────

def test_get(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/contact/10", json=api_ok(CONTACT_DICT))
    c = fb.contact.get(10)
    assert c.id == 10
    assert c.display_name == "Mamie Kipic"


# ── Contact.create ────────────────────────────────────────────────────────────

def test_create(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/",
        method="POST",
        json=api_ok(CONTACT_MINIMAL),
    )
    c = fb.contact.create(display_name="Sandy Kilo", first_name="Sandy", last_name="Kilo")
    assert c.id == 11
    assert c.display_name == "Sandy Kilo"


# ── Contact.update ────────────────────────────────────────────────────────────

def test_update(fb, httpx_mock):
    updated = dict(CONTACT_DICT, company="Freebox")
    httpx_mock.add_response(
        url=f"{API}/contact/10",
        method="PUT",
        json=api_ok(updated),
    )
    c = fb.contact.update(10, company="Freebox")
    assert c.company == "Freebox"


# ── Contact.delete ────────────────────────────────────────────────────────────

def test_delete(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/10",
        method="DELETE",
        json=api_ok(None),
    )
    fb.contact.delete(10)


# ── Sub-resource list per contact ─────────────────────────────────────────────

def test_numbers(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/10/numbers/",
        json=api_ok([NUMBER_DICT]),
    )
    nums = fb.contact.numbers(10)
    assert len(nums) == 1
    assert nums[0].number == "0612345678"


def test_addresses(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/10/addresses/",
        json=api_ok([ADDRESS_DICT]),
    )
    addrs = fb.contact.addresses(10)
    assert len(addrs) == 1
    assert addrs[0].city == "Paris"


def test_urls(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/10/urls/",
        json=api_ok([URL_DICT]),
    )
    urls = fb.contact.urls(10)
    assert len(urls) == 1
    assert urls[0].url == "http://www.example.com/"


def test_emails(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/contact/10/emails/",
        json=api_ok([EMAIL_DICT]),
    )
    emails = fb.contact.emails(10)
    assert len(emails) == 1
    assert emails[0].email == "mamie@example.org"


# ── Numbers CRUD ──────────────────────────────────────────────────────────────

def test_get_number(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/number/1", json=api_ok(NUMBER_DICT))
    n = fb.contact.get_number(1)
    assert n.id == 1
    assert n.number == "0612345678"


def test_create_number(fb, httpx_mock):
    new_num = dict(NUMBER_DICT, id=18, number="0144456789")
    httpx_mock.add_response(
        url=f"{API}/number/",
        method="POST",
        json=api_ok(new_num),
    )
    n = fb.contact.create_number(10, "0144456789", "fixed")
    assert n.id == 18
    assert n.number == "0144456789"


def test_update_number(fb, httpx_mock):
    updated = dict(NUMBER_DICT, number="0655667788", type="mobile")
    httpx_mock.add_response(
        url=f"{API}/number/1",
        method="PUT",
        json=api_ok(updated),
    )
    n = fb.contact.update_number(1, number="0655667788", type="mobile")
    assert n.number == "0655667788"
    assert n.type == "mobile"


def test_delete_number(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/number/1",
        method="DELETE",
        json=api_ok(None),
    )
    fb.contact.delete_number(1)


# ── Addresses CRUD ────────────────────────────────────────────────────────────

def test_get_address(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/address/2", json=api_ok(ADDRESS_DICT))
    a = fb.contact.get_address(2)
    assert a.id == 2
    assert a.city == "Paris"


def test_create_address(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/address/",
        method="POST",
        json=api_ok(ADDRESS_DICT),
    )
    a = fb.contact.create_address(10, type="home", city="Paris")
    assert a.city == "Paris"


def test_update_address(fb, httpx_mock):
    updated = dict(ADDRESS_DICT, city="Lyon")
    httpx_mock.add_response(
        url=f"{API}/address/2",
        method="PUT",
        json=api_ok(updated),
    )
    a = fb.contact.update_address(2, city="Lyon")
    assert a.city == "Lyon"


def test_delete_address(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/address/2",
        method="DELETE",
        json=api_ok(None),
    )
    fb.contact.delete_address(2)


# ── URLs CRUD ─────────────────────────────────────────────────────────────────

def test_get_url(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/url/3", json=api_ok(URL_DICT))
    u = fb.contact.get_url(3)
    assert u.url == "http://www.example.com/"


def test_create_url(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/url/",
        method="POST",
        json=api_ok(URL_DICT),
    )
    u = fb.contact.create_url(10, "http://www.example.com/")
    assert u.type == "site"


def test_update_url(fb, httpx_mock):
    updated = dict(URL_DICT, url="https://new.example.com/")
    httpx_mock.add_response(
        url=f"{API}/url/3",
        method="PUT",
        json=api_ok(updated),
    )
    u = fb.contact.update_url(3, url="https://new.example.com/")
    assert u.url == "https://new.example.com/"


def test_delete_url(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/url/3",
        method="DELETE",
        json=api_ok(None),
    )
    fb.contact.delete_url(3)


# ── Emails CRUD ───────────────────────────────────────────────────────────────

def test_get_email(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/email/4", json=api_ok(EMAIL_DICT))
    e = fb.contact.get_email(4)
    assert e.email == "mamie@example.org"


def test_create_email(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/email/",
        method="POST",
        json=api_ok(EMAIL_DICT),
    )
    e = fb.contact.create_email(10, "mamie@example.org")
    assert e.type == "home"


def test_update_email(fb, httpx_mock):
    updated = dict(EMAIL_DICT, email="new@example.org")
    httpx_mock.add_response(
        url=f"{API}/email/4",
        method="PUT",
        json=api_ok(updated),
    )
    e = fb.contact.update_email(4, email="new@example.org")
    assert e.email == "new@example.org"


def test_delete_email(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/email/4",
        method="DELETE",
        json=api_ok(None),
    )
    fb.contact.delete_email(4)


# ── Property ──────────────────────────────────────────────────────────────────

def test_freebox_contact_property(fb):
    assert isinstance(fb.contact, Contact)
