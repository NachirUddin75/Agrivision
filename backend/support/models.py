from django.conf import settings
from django.db import models


class SupportRequest(models.Model):

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("replied", "Replied"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_requests",
    )

    subject = models.CharField(
        max_length=200
    )

    message = models.TextField()

    # Kept for compatibility with existing support requests
    admin_reply = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.user.username}"


class SupportReply(models.Model):

    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    message = models.TextField()

    is_admin = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        sender = "Admin" if self.is_admin else "User"

        return (
            f"{sender} reply - "
            f"{self.support_request.subject}"
        )
