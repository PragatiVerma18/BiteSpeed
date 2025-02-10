from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["id", "phone_number", "email", "linked_id", "link_precedence"]
    list_filter = [
        "link_precedence",
    ]
    search_fields = [
        "id",
        "phone_number",
        "email",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]
