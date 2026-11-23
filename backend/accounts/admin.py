from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # ==================================================
    # USER LIST
    # ==================================================

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_email_verified",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    # ==================================================
    # SEARCH
    # ==================================================

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    # ==================================================
    # FILTERS
    # ==================================================

    list_filter = (
        "is_email_verified",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    # ==================================================
    # SORTING
    # ==================================================

    ordering = (
        "-created_at",
    )

    # ==================================================
    # EDIT USER
    # ==================================================

    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password",
                )
            },
        ),

        (
            "Agrivision Account Status",
            {
                "fields": (
                    "is_email_verified",
                    "is_active",
                )
            },
        ),

        (
            "Admin & Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            "OTP Information",
            {
                "fields": (
                    "otp",
                    "otp_created_at",
                )
            },
        ),

        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                )
            },
        ),
    )

    # ==================================================
    # READ-ONLY FIELDS
    # ==================================================

    readonly_fields = (
        "created_at",
        "last_login",
        "date_joined",
    )

    # ==================================================
    # ADD USER
    # ==================================================

    add_fieldsets = (
        (
            "Create Agrivision User",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),

        (
            "Account Status",
            {
                "classes": ("wide",),
                "fields": (
                    "is_active",
                    "is_email_verified",
                ),
            },
        ),

        (
            "Admin Permissions",
            {
                "classes": ("wide",),
                "fields": (
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    # ==================================================
    # PAGINATION
    # ==================================================

    list_per_page = 20