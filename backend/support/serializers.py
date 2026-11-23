from rest_framework import serializers

from .models import SupportRequest, SupportReply


class SupportReplySerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    sender = serializers.SerializerMethodField()

    class Meta:
        model = SupportReply

        fields = [
            "id",
            "username",
            "sender",
            "message",
            "is_admin",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "username",
            "sender",
            "is_admin",
            "created_at",
        ]

    def get_sender(self, obj):
        if obj.is_admin:
            return "Admin"

        return "You"


class SupportRequestSerializer(serializers.ModelSerializer):

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    replies = SupportReplySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = SupportRequest

        fields = [
            "id",
            "username",
            "subject",
            "message",
            "admin_reply",
            "status",
            "status_display",
            "replies",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "username",
            "admin_reply",
            "status",
            "status_display",
            "replies",
            "created_at",
            "updated_at",
        ]