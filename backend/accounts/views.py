import os
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import signing
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
    ForgotPasswordRequestSerializer,
    VerifyPasswordResetOTPSerializer,
    ResetPasswordSerializer,
)

from .email_service import (
    send_verification_email,
    send_login_otp_email,
    send_email_verification_success_email,
    send_password_changed_success_email,
)


User = get_user_model()


# =========================================================
# EMAIL VERIFICATION SETTINGS
# =========================================================

VERIFICATION_SALT = "agrivision-email-verification"

# Verification link valid for 24 hours
VERIFICATION_MAX_AGE = 60 * 60 * 24


# =========================================================
# REGISTER
# =========================================================

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            # Create inactive/unverified user
            user = serializer.save()

            # Create secure verification token
            token = signing.dumps(
                {
                    "user_id": user.id,
                    "email": user.email,
                },
                salt=VERIFICATION_SALT,
            )

            # Frontend verification URL
            frontend_url = os.getenv(
                "FRONTEND_URL",
                "http://localhost:5173"
            )

            verification_url = (
                f"{frontend_url}/verify-email.html?token={token}"
            )

            # Send verification email
            email_sent = send_verification_email(
                user,
                verification_url,
            )

            # If email failed, remove the newly created user
            if not email_sent:
                user.delete()

                return Response(
                    {
                        "message": (
                            "Registration failed because "
                            "the verification email could not be sent."
                        )
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            return Response(
                {
                    "message": (
                        "Registration successful. "
                        "Please check your email and verify your account."
                    ),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================
# VERIFY EMAIL
# =========================================================

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        token = request.data.get("token")

        if not token:
            return Response(
                {
                    "message": "Verification token is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate verification token
        try:
            data = signing.loads(
                token,
                salt=VERIFICATION_SALT,
                max_age=VERIFICATION_MAX_AGE,
            )

        except signing.BadSignature:
            return Response(
                {
                    "message": (
                        "Invalid or expired verification link."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = data.get("user_id")
        email = data.get("email")

        # Find user
        try:
            user = User.objects.get(
                id=user_id,
                email=email,
            )

        except User.DoesNotExist:
            return Response(
                {
                    "message": "User account not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Already verified
        if user.is_email_verified:
            return Response(
                {
                    "message": "Email is already verified."
                },
                status=status.HTTP_200_OK,
            )

        # Activate account
        user.is_email_verified = True
        user.is_active = True

        user.save(
            update_fields=[
                "is_email_verified",
                "is_active",
            ]
        )

        # -------------------------------------------------
        # Send verification-success email
        # -------------------------------------------------
        # This is sent only after the database update
        # successfully completes.
        success_email_sent = (
            send_email_verification_success_email(user)
        )

        if not success_email_sent:
            print(
                "Warning: Email verification succeeded, "
                "but the verification success email could not be sent."
            )

        return Response(
            {
                "message": (
                    "Email verified successfully. "
                    "Your Agrivision account is now active."
                )
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# CHECK USERNAME
# =========================================================

class CheckUsernameView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):

        username = request.query_params.get(
            "username",
            ""
        ).strip()

        if not username:
            return Response(
                {
                    "available": False,
                    "message": "Username is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        exists = User.objects.filter(
            username__iexact=username
        ).exists()

        if exists:
            return Response(
                {
                    "available": False,
                    "message": "Username already exists."
                }
            )

        return Response(
            {
                "available": True,
                "message": "Username is available."
            }
        )


# =========================================================
# PASSWORD LOGIN
# =========================================================

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",

                "access": str(
                    refresh.access_token
                ),

                "refresh": str(
                    refresh
                ),

                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# REQUEST LOGIN OTP
# =========================================================

class RequestOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = RequestOTPSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        # Generate secure 6-digit OTP
        otp = str(
            random.SystemRandom().randint(
                100000,
                999999
            )
        )

        # Store OTP
        user.otp = otp
        user.otp_created_at = timezone.now()

        user.save(
            update_fields=[
                "otp",
                "otp_created_at",
            ]
        )

        # Send OTP email
        email_sent = send_login_otp_email(
            user,
            otp,
        )

        if not email_sent:
            return Response(
                {
                    "message": (
                        "Unable to send OTP. "
                        "Please try again."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "message": (
                    "OTP sent successfully. "
                    "Please check your email."
                ),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# VERIFY LOGIN OTP
# =========================================================

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = VerifyOTPSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        # Check OTP expiry
        if (
            not user.otp_created_at
            or timezone.now()
            > user.otp_created_at
            + timedelta(minutes=10)
        ):
            user.otp = None
            user.otp_created_at = None

            user.save(
                update_fields=[
                    "otp",
                    "otp_created_at",
                ]
            )

            return Response(
                {
                    "message": (
                        "OTP has expired. "
                        "Please request a new OTP."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # OTP is valid
        user.otp = None
        user.otp_created_at = None

        user.save(
            update_fields=[
                "otp",
                "otp_created_at",
            ]
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "OTP login successful.",

                "access": str(
                    refresh.access_token
                ),

                "refresh": str(
                    refresh
                ),

                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# FORGOT PASSWORD - REQUEST OTP
# =========================================================

class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = ForgotPasswordRequestSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        # Generate secure 6-digit OTP
        otp = str(
            random.SystemRandom().randint(
                100000,
                999999
            )
        )

        user.otp = otp
        user.otp_created_at = timezone.now()

        user.save(
            update_fields=[
                "otp",
                "otp_created_at",
            ]
        )

        # Send password reset OTP
        email_sent = send_login_otp_email(
            user,
            otp,
        )

        if not email_sent:
            return Response(
                {
                    "message": (
                        "Unable to send password reset OTP. "
                        "Please try again."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "message": (
                    "Password reset OTP sent successfully. "
                    "Please check your email."
                )
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# VERIFY PASSWORD RESET OTP
# =========================================================

class VerifyPasswordResetOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = VerifyPasswordResetOTPSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        # Check OTP expiry
        if (
            not user.otp_created_at
            or timezone.now()
            > user.otp_created_at
            + timedelta(minutes=10)
        ):
            user.otp = None
            user.otp_created_at = None

            user.save(
                update_fields=[
                    "otp",
                    "otp_created_at",
                ]
            )

            return Response(
                {
                    "message": (
                        "OTP has expired. "
                        "Please request a new OTP."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "OTP verified successfully.",
                "username": user.username,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# RESET PASSWORD
# =========================================================

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = ResetPasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        # -------------------------------------------------
        # Check OTP expiry
        # -------------------------------------------------

        if (
            not user.otp_created_at
            or timezone.now()
            > user.otp_created_at
            + timedelta(minutes=10)
        ):
            user.otp = None
            user.otp_created_at = None

            user.save(
                update_fields=[
                    "otp",
                    "otp_created_at",
                ]
            )

            return Response(
                {
                    "message": (
                        "OTP has expired. "
                        "Please request a new OTP."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Change password
        # -------------------------------------------------

        user.set_password(
            serializer.validated_data["new_password"]
        )

        # Clear OTP after successful password reset
        user.otp = None
        user.otp_created_at = None

        user.save(
            update_fields=[
                "password",
                "otp",
                "otp_created_at",
            ]
        )

        # -------------------------------------------------
        # Send password changed success email
        # -------------------------------------------------
        # The password has already been successfully saved
        # before this email is attempted.
        success_email_sent = (
            send_password_changed_success_email(user)
        )

        if not success_email_sent:
            print(
                "Warning: Password was changed successfully, "
                "but the password success email could not be sent."
            )

        return Response(
            {
                "message": (
                    "Password changed successfully."
                )
            },
            status=status.HTTP_200_OK,
        )

# =========================================================
# DEBUG JWT
# =========================================================

class DebugJWTView(APIView):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [AllowAny]

    def get(self, request):

        auth_result = JWTAuthentication().authenticate(request)

        if auth_result is None:
            return Response(
                {
                    "authenticated": False,
                    "message": "JWT authentication failed.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user, token = auth_result

        return Response(
            {
                "authenticated": True,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token_type": token.get("token_type"),
            },
            status=status.HTTP_200_OK,
        )