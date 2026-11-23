from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data["email"],
            password=validated_data["password"],
        )

        user.is_active = False
        user.is_email_verified = False
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        login_value = attrs.get("username")
        password = attrs.get("password")

        user = None

        # Try login using username
        user = authenticate(
            username=login_value,
            password=password,
        )

        # If username login fails, try email login
        if user is None:
            email_user = User.objects.filter(
                email__iexact=login_value
            ).first()

            if email_user:
                user = authenticate(
                    username=email_user.username,
                    password=password,
                )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username/email or password."
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email before logging in."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is not active."
            )

        attrs["user"] = user

        return attrs


class RequestOTPSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, attrs):
        login_value = attrs.get("username")

        # Search by username
        user = User.objects.filter(
            username__iexact=login_value
        ).first()

        # If not found, search by email
        if user is None:
            user = User.objects.filter(
                email__iexact=login_value
            ).first()

        if user is None:
            raise serializers.ValidationError(
                "No account was found with this username or email."
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email before using OTP login."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is not active."
            )

        attrs["user"] = user

        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6
    )

    def validate(self, attrs):
        login_value = attrs.get("username")
        otp = attrs.get("otp")

        # Search by username
        user = User.objects.filter(
            username__iexact=login_value
        ).first()

        # If not found, search by email
        if user is None:
            user = User.objects.filter(
                email__iexact=login_value
            ).first()

        if user is None:
            raise serializers.ValidationError(
                "No account was found with this username or email."
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email before using OTP login."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is not active."
            )

        if not user.otp:
            raise serializers.ValidationError(
                "No OTP was found. Please request a new OTP."
            )

        if user.otp != otp:
            raise serializers.ValidationError(
                "Invalid OTP."
            )

        attrs["user"] = user

        return attrs


class ForgotPasswordRequestSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, attrs):
        login_value = attrs.get("username")

        # Search by username
        user = User.objects.filter(
            username__iexact=login_value
        ).first()

        # If not found, search by email
        if user is None:
            user = User.objects.filter(
                email__iexact=login_value
            ).first()

        if user is None:
            raise serializers.ValidationError(
                "No account was found with this username or email."
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email before resetting your password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is not active."
            )

        attrs["user"] = user

        return attrs


class VerifyPasswordResetOTPSerializer(serializers.Serializer):
    username = serializers.CharField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6
    )

    def validate(self, attrs):
        login_value = attrs.get("username")
        otp = attrs.get("otp")

        # Search by username
        user = User.objects.filter(
            username__iexact=login_value
        ).first()

        # If not found, search by email
        if user is None:
            user = User.objects.filter(
                email__iexact=login_value
            ).first()

        if user is None:
            raise serializers.ValidationError(
                "No account was found with this username or email."
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email before resetting your password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is not active."
            )

        if not user.otp:
            raise serializers.ValidationError(
                "No OTP was found. Please request a new OTP."
            )

        if user.otp != otp:
            raise serializers.ValidationError(
                "Invalid OTP."
            )

        attrs["user"] = user

        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate(self, attrs):
        login_value = attrs.get("username")
        otp = attrs.get("otp")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        # Find user by username
        user = User.objects.filter(
            username__iexact=login_value
        ).first()

        # If not found, find user by email
        if user is None:
            user = User.objects.filter(
                email__iexact=login_value
            ).first()

        if user is None:
            raise serializers.ValidationError(
                "No account was found with this username or email."
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email before resetting your password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is not active."
            )

        if not user.otp:
            raise serializers.ValidationError(
                "No OTP was found. Please request a new OTP."
            )

        # Check OTP
        if user.otp != otp:
            raise serializers.ValidationError(
                "Invalid OTP."
            )

        if not user.otp_created_at:
            raise serializers.ValidationError(
                "OTP information is missing. Please request a new OTP."
            )

        # Check OTP expiry
        from django.utils import timezone
        from datetime import timedelta

        if (
            timezone.now()
            > user.otp_created_at + timedelta(minutes=10)
        ):
            raise serializers.ValidationError(
                "OTP has expired. Please request a new OTP."
            )

        # Check password confirmation
        if new_password != confirm_password:
            raise serializers.ValidationError(
                "Passwords do not match."
            )

        # Prevent using the previous/current password
        if user.check_password(new_password):
            raise serializers.ValidationError(
                "You cannot use your previous password. "
                "Please enter a new password."
            )

        attrs["user"] = user

        return attrs