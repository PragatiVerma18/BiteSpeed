from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "phone_number",
            "email",
            "link_precedence",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
