"""Freebox contact (phonebook) API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── Sub-objects ───────────────────────────────────────────────────────────────

@dataclass
class ContactNumber:
    """A phone number belonging to a contact."""

    id: int
    contact_id: int
    type: str
    number: str
    is_default: bool
    is_own: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ContactNumber:
        return cls(
            id=d.get("id", 0),
            contact_id=d.get("contact_id", 0),
            type=d.get("type", ""),
            number=d.get("number", ""),
            is_default=d.get("is_default", False),
            is_own=d.get("is_own", False),
        )


@dataclass
class ContactAddress:
    """A postal address belonging to a contact."""

    id: int
    contact_id: int
    type: str
    number: str
    street: str
    street2: str
    city: str
    zipcode: str
    country: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ContactAddress:
        return cls(
            id=d.get("id", 0),
            contact_id=d.get("contact_id", 0),
            type=d.get("type", ""),
            number=d.get("number", ""),
            street=d.get("street", ""),
            street2=d.get("street2", ""),
            city=d.get("city", ""),
            zipcode=d.get("zipcode", ""),
            country=d.get("country", ""),
        )


@dataclass
class ContactUrl:
    """A URL belonging to a contact."""

    id: int
    contact_id: int
    type: str
    url: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ContactUrl:
        return cls(
            id=d.get("id", 0),
            contact_id=d.get("contact_id", 0),
            type=d.get("type", ""),
            url=d.get("url", ""),
        )


@dataclass
class ContactEmail:
    """An email address belonging to a contact."""

    id: int
    contact_id: int
    type: str
    email: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ContactEmail:
        return cls(
            id=d.get("id", 0),
            contact_id=d.get("contact_id", 0),
            type=d.get("type", ""),
            email=d.get("email", ""),
        )


@dataclass
class ContactEntry:
    """A contact entry in the Freebox phonebook."""

    id: int
    display_name: str
    first_name: str
    last_name: str
    company: str
    photo_url: str
    last_update: int
    birthday: str
    notes: str
    numbers: list[ContactNumber]
    addresses: list[ContactAddress]
    urls: list[ContactUrl]
    emails: list[ContactEmail]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ContactEntry:
        return cls(
            id=d.get("id", 0),
            display_name=d.get("display_name", ""),
            first_name=d.get("first_name", ""),
            last_name=d.get("last_name", ""),
            company=d.get("company", ""),
            photo_url=d.get("photo_url", ""),
            last_update=d.get("last_update", 0),
            birthday=d.get("birthday", ""),
            notes=d.get("notes", ""),
            numbers=[ContactNumber._from_dict(n) for n in d.get("numbers") or []],
            addresses=[ContactAddress._from_dict(a) for a in d.get("addresses") or []],
            urls=[ContactUrl._from_dict(u) for u in d.get("urls") or []],
            emails=[ContactEmail._from_dict(e) for e in d.get("emails") or []],
        )


# ── API class ─────────────────────────────────────────────────────────────────

class Contact:
    """Freebox phonebook (contact) API.

    Obtained via ``fb.contact``::

        contacts = fb.contact.list()
        for c in contacts:
            print(c.display_name, [n.number for n in c.numbers])
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Contacts ───────────────────────────────────────────────────────────────

    def list(
        self,
        *,
        start: int | None = None,
        limit: int | None = None,
        group_id: int | None = None,
    ) -> list[ContactEntry]:
        """Return all contacts.

        ``start`` and ``limit`` can be used for pagination.
        ``group_id`` filters by contact group.
        """
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit
        if group_id is not None:
            params["group_id"] = group_id
        result = self._client.get("contact/", params=params)
        return [ContactEntry._from_dict(c) for c in result] if result else []

    def get(self, contact_id: int) -> ContactEntry:
        """Return the contact with the given id."""
        return ContactEntry._from_dict(self._client.get(f"contact/{contact_id}"))

    def create(self, **kwargs: Any) -> ContactEntry:
        """Create a new contact.

        Keyword arguments correspond to ``ContactEntry`` fields
        (e.g. ``display_name``, ``first_name``, ``last_name``, ``company``).
        """
        return ContactEntry._from_dict(self._client.post("contact/", json=kwargs))

    def update(self, contact_id: int, **kwargs: Any) -> ContactEntry:
        """Update the contact with the given id."""
        return ContactEntry._from_dict(
            self._client.put(f"contact/{contact_id}", json=kwargs)
        )

    def delete(self, contact_id: int) -> None:
        """Delete the contact with the given id."""
        self._client.delete(f"contact/{contact_id}")

    # ── Sub-resource list per contact ──────────────────────────────────────────

    def numbers(self, contact_id: int) -> list[ContactNumber]:
        """Return all phone numbers for the given contact."""
        result = self._client.get(f"contact/{contact_id}/numbers/")
        return [ContactNumber._from_dict(n) for n in result] if result else []

    def addresses(self, contact_id: int) -> list[ContactAddress]:
        """Return all postal addresses for the given contact."""
        result = self._client.get(f"contact/{contact_id}/addresses/")
        return [ContactAddress._from_dict(a) for a in result] if result else []

    def urls(self, contact_id: int) -> list[ContactUrl]:
        """Return all URLs for the given contact."""
        result = self._client.get(f"contact/{contact_id}/urls/")
        return [ContactUrl._from_dict(u) for u in result] if result else []

    def emails(self, contact_id: int) -> list[ContactEmail]:
        """Return all email addresses for the given contact."""
        result = self._client.get(f"contact/{contact_id}/emails/")
        return [ContactEmail._from_dict(e) for e in result] if result else []

    # ── Numbers ────────────────────────────────────────────────────────────────

    def get_number(self, number_id: int) -> ContactNumber:
        """Return the phone number entry with the given id."""
        return ContactNumber._from_dict(self._client.get(f"number/{number_id}"))

    def create_number(self, contact_id: int, number: str, type: str = "fixed", **kwargs: Any) -> ContactNumber:
        """Create a new phone number for a contact."""
        return ContactNumber._from_dict(
            self._client.post("number/", json={"contact_id": contact_id, "number": number, "type": type, **kwargs})
        )

    def update_number(self, number_id: int, **kwargs: Any) -> ContactNumber:
        """Update a phone number entry."""
        return ContactNumber._from_dict(
            self._client.put(f"number/{number_id}", json=kwargs)
        )

    def delete_number(self, number_id: int) -> None:
        """Delete a phone number entry."""
        self._client.delete(f"number/{number_id}")

    # ── Addresses ──────────────────────────────────────────────────────────────

    def get_address(self, address_id: int) -> ContactAddress:
        """Return the postal address entry with the given id."""
        return ContactAddress._from_dict(self._client.get(f"address/{address_id}"))

    def create_address(self, contact_id: int, type: str = "home", **kwargs: Any) -> ContactAddress:
        """Create a new postal address for a contact."""
        return ContactAddress._from_dict(
            self._client.post("address/", json={"contact_id": contact_id, "type": type, **kwargs})
        )

    def update_address(self, address_id: int, **kwargs: Any) -> ContactAddress:
        """Update a postal address entry."""
        return ContactAddress._from_dict(
            self._client.put(f"address/{address_id}", json=kwargs)
        )

    def delete_address(self, address_id: int) -> None:
        """Delete a postal address entry."""
        self._client.delete(f"address/{address_id}")

    # ── URLs ───────────────────────────────────────────────────────────────────

    def get_url(self, url_id: int) -> ContactUrl:
        """Return the URL entry with the given id."""
        return ContactUrl._from_dict(self._client.get(f"url/{url_id}"))

    def create_url(self, contact_id: int, url: str, type: str = "site", **kwargs: Any) -> ContactUrl:
        """Create a new URL for a contact."""
        return ContactUrl._from_dict(
            self._client.post("url/", json={"contact_id": contact_id, "url": url, "type": type, **kwargs})
        )

    def update_url(self, url_id: int, **kwargs: Any) -> ContactUrl:
        """Update a URL entry."""
        return ContactUrl._from_dict(
            self._client.put(f"url/{url_id}", json=kwargs)
        )

    def delete_url(self, url_id: int) -> None:
        """Delete a URL entry."""
        self._client.delete(f"url/{url_id}")

    # ── Emails ─────────────────────────────────────────────────────────────────

    def get_email(self, email_id: int) -> ContactEmail:
        """Return the email entry with the given id."""
        return ContactEmail._from_dict(self._client.get(f"email/{email_id}"))

    def create_email(self, contact_id: int, email: str, type: str = "home", **kwargs: Any) -> ContactEmail:
        """Create a new email address for a contact."""
        return ContactEmail._from_dict(
            self._client.post("email/", json={"contact_id": contact_id, "email": email, "type": type, **kwargs})
        )

    def update_email(self, email_id: int, **kwargs: Any) -> ContactEmail:
        """Update an email address entry."""
        return ContactEmail._from_dict(
            self._client.put(f"email/{email_id}", json=kwargs)
        )

    def delete_email(self, email_id: int) -> None:
        """Delete an email address entry."""
        self._client.delete(f"email/{email_id}")
