from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    is_email_verified = models.BooleanField(
        default=False
    )

    otp = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    otp_created_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email