from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    VerifyEmailView,
    CheckUsernameView,
    LoginView,
    RequestOTPView,
    VerifyOTPView,
    ForgotPasswordRequestView,
    VerifyPasswordResetOTPView,
    ResetPasswordView,
)


urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "verify-email/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),

    path(
        "check-username/",
        CheckUsernameView.as_view(),
        name="check-username",
    ),

    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    path(
    "request-otp/",
    RequestOTPView.as_view(),
    name="request-otp",
    ),

    path(
    "verify-otp/",
    VerifyOTPView.as_view(),
    name="verify-otp"
    ),

    path(
    "forgot-password/request-otp/",
    ForgotPasswordRequestView.as_view(),
    name="forgot-password-request-otp",
    ),

    path(
    "forgot-password/verify-otp/",
    VerifyPasswordResetOTPView.as_view(),
    name="forgot-password-verify-otp",
    ),

    path(
    "forgot-password/reset/",
    ResetPasswordView.as_view(),
    name="forgot-password-reset",
    ),


]