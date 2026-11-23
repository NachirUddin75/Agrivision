from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import SupportRequest, SupportReply
from .serializers import (
    SupportRequestSerializer,
    SupportReplySerializer,
)


class SupportRequestListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = SupportRequestSerializer

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return SupportRequest.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user
        )


class SupportReplyCreateView(
    generics.CreateAPIView
):

    serializer_class = SupportReplySerializer

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def create(self, request, *args, **kwargs):

        support_id = kwargs.get("support_id")

        try:
            support_request = SupportRequest.objects.get(
                id=support_id,
                user=request.user,
            )

        except SupportRequest.DoesNotExist:

            return Response(
                {
                    "message": (
                        "Support request not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        message = request.data.get(
            "message",
            ""
        ).strip()

        if not message:

            return Response(
                {
                    "message": (
                        "Reply message is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(message) > 5000:

            return Response(
                {
                    "message": (
                        "Reply cannot exceed "
                        "5000 characters."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reply = SupportReply.objects.create(
            support_request=support_request,
            user=request.user,
            message=message,
            is_admin=False,
        )

        # If the user replies after an admin response,
        # mark the ticket as in progress.
        support_request.status = "in_progress"
        support_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(reply)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
