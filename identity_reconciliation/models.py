from django.db import models


class Contact(models.Model):
    TYPE_PRIMARY = "PRIMARY"
    TYPE_SECONDARY = "SECONDARY"
    TYPE_CHOICES = (
        (TYPE_PRIMARY, "Primary"),
        (TYPE_SECONDARY, "Secondary"),
    )

    phone_number = models.CharField(max_length=15, null=True, blank=True, db_index=True)
    email = models.EmailField(null=True, blank=True, db_index=True)
    linked_id = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE
    )
    link_precedence = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_PRIMARY,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Contact {self.id} ({self.link_precedence})"
