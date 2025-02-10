from drf_yasg.utils import swagger_auto_schema

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q

from identity_reconciliation.models import Contact


class IdentifyRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True)
    phoneNumber = serializers.CharField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get("email") and not data.get("phoneNumber"):
            raise serializers.ValidationError(
                "At least one of email or phoneNumber is required."
            )
        return data


def format_response(primary_contact):
    """Formats the response to return primary and linked contacts."""
    linked_contacts = Contact.objects.filter(
        Q(linked_id=primary_contact) | Q(id=primary_contact.id)
    ).only("id", "email", "phone_number", "link_precedence")

    emails = [primary_contact.email] if primary_contact.email else []
    emails += list(
        set(
            c.email
            for c in linked_contacts
            if c.email and c.email != primary_contact.email
        )
    )

    phone_numbers = list(set(c.phone_number for c in linked_contacts if c.phone_number))
    secondary_ids = [
        c.id for c in linked_contacts if c.link_precedence == Contact.TYPE_SECONDARY
    ]

    return {
        "contact": {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_ids,
        }
    }


from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status


class IdentifyView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "phoneNumber"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    example="user@example.com",
                ),
                "phoneNumber": openapi.Schema(
                    type=openapi.TYPE_STRING, example="+1234567890"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                examples={
                    "application/json": {
                        "contact": {
                            "primaryContactId": 1,
                            "emails": ["user@example.com"],
                            "phoneNumbers": ["+1234567890"],
                            "secondaryContactIds": [2, 3],
                        }
                    }
                },
            ),
            400: openapi.Response(
                description="Validation Error",
                examples={
                    "application/json": {
                        "error": "At least one of email or phoneNumber is required."
                    }
                },
            ),
        },
    )
    def post(self, request):

        # Step 1: Validate request data
        serializer = IdentifyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        phone_number = serializer.validated_data.get("phoneNumber")

        # Step 2: Fetch all contacts linked to email or phone number in one query
        query = Q()
        if email:
            query |= Q(email=email)
        if phone_number:
            query |= Q(phone_number=phone_number)

        matching_contacts = Contact.objects.filter(query).select_related("linked_id")

        if not matching_contacts.exists():
            # No existing contacts, create a new primary contact
            new_contact = Contact.objects.create(
                email=email,
                phone_number=phone_number,
                link_precedence=Contact.TYPE_PRIMARY,
            )
            return Response(format_response(new_contact), status=status.HTTP_200_OK)

        # Step 3: Identify the primary contact
        primary_contact = (
            matching_contacts.filter(link_precedence=Contact.TYPE_PRIMARY)
            .order_by("created_at")
            .first()
        ) or matching_contacts.first()

        secondary_contacts = list(
            matching_contacts.exclude(id=primary_contact.id).filter(
                link_precedence=Contact.TYPE_SECONDARY
            )
        )

        # Step 4: Convert only the newer primary contact into secondary
        for contact in matching_contacts:
            if (
                contact.id != primary_contact.id
                and contact.link_precedence == Contact.TYPE_PRIMARY
            ):
                # Convert the newer primary contact into a secondary contact
                contact.linked_id = primary_contact
                contact.link_precedence = Contact.TYPE_SECONDARY
                contact.save(update_fields=["linked_id", "link_precedence"])
                secondary_contacts.append(contact)

        return Response(format_response(primary_contact), status=status.HTTP_200_OK)
