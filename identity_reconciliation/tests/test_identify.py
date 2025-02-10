import pytest

from rest_framework.test import APIClient
from identity_reconciliation.models import Contact


@pytest.mark.django_db
class TestIdentifyAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()

    def test_create_new_primary_contact(self):
        """New contact should be created when no match exists."""
        response = self.client.post(
            "/api/identify/",
            {"email": "lorraine@hillvalley.edu", "phoneNumber": "123456"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["contact"]["primaryContactId"] is not None
        assert response.data["contact"]["emails"] == ["lorraine@hillvalley.edu"]
        assert response.data["contact"]["phoneNumbers"] == ["123456"]
        assert response.data["contact"]["secondaryContactIds"] == []

    def test_identify_existing_contact(self):
        """Existing contact should be returned when a match is found."""

        primary = Contact.objects.create(
            email="lorraine@hillvalley.edu",
            phone_number="123456",
            link_precedence=Contact.TYPE_PRIMARY,
        )

        response = self.client.post(
            "/api/identify/", {"email": "lorraine@hillvalley.edu"}, format="json"
        )

        assert response.status_code == 200
        assert response.data["contact"]["primaryContactId"] == primary.id
        assert response.data["contact"]["emails"] == ["lorraine@hillvalley.edu"]
        assert response.data["contact"]["phoneNumbers"] == ["123456"]
        assert response.data["contact"]["secondaryContactIds"] == []

    def test_primary_contact_turning_into_secondary(self):
        """When an older primary contact is found, a newer one should turn into secondary."""

        old_primary = Contact.objects.create(
            id=11,
            email="george@hillvalley.edu",
            phone_number="919191",
            link_precedence=Contact.TYPE_PRIMARY,
        )
        new_primary = Contact.objects.create(
            id=27,
            email="biffsucks@hillvalley.edu",
            phone_number="717171",
            link_precedence=Contact.TYPE_PRIMARY,
        )

        response = self.client.post(
            "/api/identify/",
            {"email": "george@hillvalley.edu", "phoneNumber": "717171"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["contact"]["primaryContactId"] == old_primary.id
        assert set(response.data["contact"]["emails"]) == {
            "george@hillvalley.edu",
            "biffsucks@hillvalley.edu",
        }
        assert set(response.data["contact"]["phoneNumbers"]) == {"919191", "717171"}
        assert response.data["contact"]["secondaryContactIds"] == [new_primary.id]

    def test_invalid_request_returns_400(self):
        """Invalid requests without email or phoneNumber should return 400."""

        response = self.client.post("/api/identify/", {}, format="json")

        assert response.status_code == 400
        assert "non_field_errors" in response.data
