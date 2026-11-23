import os
import requests
from django.conf import settings
from django.utils.html import strip_tags
import re


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

BREVO_SENDER_NAME = "Agrivision"
BREVO_SENDER_EMAIL = "agrivision.new.official@gmail.com"


# =========================================================
# COMMON BREVO EMAIL SENDER
# =========================================================

def send_brevo_email(user, subject, html_content):
    api_key = os.getenv("BREVO_API_KEY")

    if not api_key:
        if settings.DEBUG:
            # Registration & OTP are usable on local PCs with no email API.
            # Terminal output is restricted to DEBUG mode and should not be shared.
            print("\n=== AGRIVISION LOCAL EMAIL (development only) ===")
            print("Recipient:", user.email)
            print("Subject:", subject)
            print(strip_tags(html_content).strip())
            for url in re.findall(r'href=["\'](https?://[^"\']+)["\']', html_content):
                if "verify-email" in url:
                    print("Open verification link:", url)
            print("=== END LOCAL EMAIL ===\n")
            return True
        return False

    payload = {
        "sender": {
            "name": BREVO_SENDER_NAME,
            "email": BREVO_SENDER_EMAIL,
        },
        "to": [
            {
                "email": user.email,
                "name": user.get_full_name() or user.username,
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        response = requests.post(
            BREVO_API_URL,
            headers=headers,
            json=payload,
            timeout=15,
        )

        print("Brevo response:", response.status_code)
        print("Brevo body:", response.text)

        if response.status_code in [200, 201, 202]:
            return True

        return False

    except requests.RequestException as error:
        print("Brevo request error:", error)
        return False


# =========================================================
# EMAIL VERIFICATION EMAIL
# =========================================================

def send_verification_email(user, verification_url):

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Verify Your Agrivision Account</title>

    </head>


    <body style="
        margin:0;
        padding:0;
        background:#f4f8f3;
        font-family:Arial,Helvetica,sans-serif;
    ">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:white;
            border-radius:16px;
            overflow:hidden;
            box-shadow:0 10px 30px rgba(46,125,50,0.10);
        ">


            <!-- HEADER -->

            <div style="
                background:#2e7d32;
                padding:35px;
                text-align:center;
                color:white;
            ">

                <div style="
                    font-size:42px;
                    margin-bottom:8px;
                ">
                    🌱
                </div>

                <h1 style="
                    margin:0;
                    font-size:32px;
                ">
                    Agrivision
                </h1>

                <p style="
                    margin:10px 0 0;
                    font-size:14px;
                ">
                    Smart Farming. Better Decisions.
                </p>

            </div>


            <!-- CONTENT -->

            <div style="
                padding:40px;
                text-align:center;
            ">

                <div style="
                    font-size:42px;
                    margin-bottom:10px;
                ">
                    ✉️
                </div>

                <h2 style="
                    color:#263238;
                    margin:10px 0 15px;
                ">
                    Welcome to Agrivision!
                </h2>

                <p style="
                    color:#607d8b;
                    font-size:16px;
                    line-height:1.7;
                ">
                    Thanks for creating your account.
                    Please verify your email address to continue.
                </p>


                <!-- BUTTON -->

                <a href="{verification_url}"
                   style="
                       display:inline-block;
                       margin-top:20px;
                       padding:14px 28px;
                       background:#2e7d32;
                       color:white;
                       text-decoration:none;
                       border-radius:8px;
                       font-weight:bold;
                       font-size:15px;
                   ">
                    Verify My Email →
                </a>


                <p style="
                    margin-top:30px;
                    color:#90a4ae;
                    font-size:13px;
                ">
                    This verification link is valid for 24 hours.
                </p>

            </div>


            <!-- FOOTER -->

            <div style="
                padding:20px;
                text-align:center;
                background:#f5f7f5;
                color:#78909c;
                font-size:12px;
            ">

                © Agrivision — Analyze Soil. Grow Smarter.

            </div>

        </div>

    </body>

    </html>
    """

    return send_brevo_email(
        user=user,
        subject="Verify your Agrivision account",
        html_content=html_content,
    )


# =========================================================
# LOGIN OTP EMAIL
# =========================================================

def send_login_otp_email(user, otp):

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Agrivision Login OTP</title>

    </head>


    <body style="
        margin:0;
        padding:0;
        background:#f4f8f3;
        font-family:Arial,Helvetica,sans-serif;
    ">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:white;
            border-radius:16px;
            overflow:hidden;
            box-shadow:0 10px 30px rgba(46,125,50,0.10);
        ">


            <!-- HEADER -->

            <div style="
                background:#2e7d32;
                padding:35px;
                text-align:center;
                color:white;
            ">

                <div style="
                    font-size:42px;
                    margin-bottom:8px;
                ">
                    🌱
                </div>

                <h1 style="
                    margin:0;
                    font-size:32px;
                ">
                    Agrivision
                </h1>

                <p style="
                    margin:10px 0 0;
                    font-size:14px;
                ">
                    Secure Login
                </p>

            </div>


            <!-- CONTENT -->

            <div style="
                padding:40px;
                text-align:center;
            ">

                <div style="
                    font-size:42px;
                    margin-bottom:10px;
                ">
                    🔐
                </div>

                <h2 style="
                    color:#263238;
                    margin:10px 0 15px;
                ">
                    Login Verification
                </h2>

                <p style="
                    color:#607d8b;
                    font-size:16px;
                    line-height:1.7;
                ">
                    Use the following OTP to complete your
                    Agrivision login.
                </p>


                <!-- OTP -->

                <div style="
                    margin:30px auto;
                    padding:18px;
                    max-width:220px;
                    background:#e8f5e9;
                    border-radius:10px;
                    color:#2e7d32;
                    font-size:32px;
                    font-weight:bold;
                    letter-spacing:8px;
                ">
                    {otp}
                </div>


                <p style="
                    color:#90a4ae;
                    font-size:13px;
                ">
                    This OTP is valid for 10 minutes.
                </p>

            </div>


            <!-- FOOTER -->

            <div style="
                padding:20px;
                text-align:center;
                background:#f5f7f5;
                color:#78909c;
                font-size:12px;
            ">

                © Agrivision — Analyze Soil. Grow Smarter.

            </div>

        </div>

    </body>

    </html>
    """

    return send_brevo_email(
        user=user,
        subject="Your Agrivision Login OTP",
        html_content=html_content,
    )


# =========================================================
# EMAIL VERIFICATION SUCCESS EMAIL
# =========================================================

def send_email_verification_success_email(user):

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Email Verified Successfully</title>

    </head>


    <body style="
        margin:0;
        padding:0;
        background:#f4f8f3;
        font-family:Arial,Helvetica,sans-serif;
    ">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:white;
            border-radius:16px;
            overflow:hidden;
            box-shadow:0 10px 30px rgba(46,125,50,0.10);
        ">


            <!-- HEADER -->

            <div style="
                background:#2e7d32;
                padding:35px;
                text-align:center;
                color:white;
            ">

                <div style="
                    font-size:42px;
                    margin-bottom:8px;
                ">
                    🌱
                </div>

                <h1 style="
                    margin:0;
                    font-size:32px;
                ">
                    Agrivision
                </h1>

                <p style="
                    margin:10px 0 0;
                    font-size:14px;
                ">
                    Smart Farming. Better Decisions.
                </p>

            </div>


            <!-- SUCCESS CONTENT -->

            <div style="
                padding:45px 40px;
                text-align:center;
            ">

                <!-- SUCCESS ICON -->

                <div style="
                    width:76px;
                    height:76px;
                    margin:0 auto 20px;
                    border-radius:50%;
                    background:#e8f5e9;
                    color:#2e7d32;
                    font-size:42px;
                    line-height:76px;
                    font-weight:bold;
                ">
                    ✓
                </div>


                <h2 style="
                    color:#263238;
                    margin:0;
                    font-size:27px;
                ">
                    Email Verified Successfully!
                </h2>


                <p style="
                    margin-top:20px;
                    color:#607d8b;
                    font-size:16px;
                    line-height:1.7;
                ">

                    Congratulations
                    <strong>
                        {user.first_name or user.username}
                    </strong>!

                </p>


                <p style="
                    color:#607d8b;
                    font-size:15px;
                    line-height:1.7;
                ">
                    Your Agrivision account has been successfully
                    verified and is now ready to use.
                </p>


                <!-- WELCOME BOX -->

                <div style="
                    margin-top:30px;
                    padding:20px;
                    background:#e8f5e9;
                    border-radius:12px;
                    color:#2e7d32;
                    font-size:15px;
                    font-weight:bold;
                ">

                    🌱 Welcome to Agrivision

                </div>


                <p style="
                    margin-top:25px;
                    color:#90a4ae;
                    font-size:13px;
                    line-height:1.6;
                ">
                    You can now sign in and start using
                    Agrivision's smart farming features.
                </p>

            </div>


            <!-- FOOTER -->

            <div style="
                padding:20px;
                text-align:center;
                background:#f5f7f5;
                color:#78909c;
                font-size:12px;
            ">

                © Agrivision — Analyze Soil. Grow Smarter.

            </div>

        </div>

    </body>

    </html>
    """

    return send_brevo_email(
        user=user,
        subject="Your Agrivision email has been verified",
        html_content=html_content,
    )


# =========================================================
# PASSWORD CHANGED SUCCESS EMAIL
# =========================================================

def send_password_changed_success_email(user):

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Password Changed Successfully</title>

    </head>


    <body style="
        margin:0;
        padding:0;
        background:#f4f8f3;
        font-family:Arial,Helvetica,sans-serif;
    ">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:white;
            border-radius:16px;
            overflow:hidden;
            box-shadow:0 10px 30px rgba(46,125,50,0.10);
        ">


            <!-- HEADER -->

            <div style="
                background:#2e7d32;
                padding:35px;
                text-align:center;
                color:white;
            ">

                <div style="
                    font-size:42px;
                    margin-bottom:8px;
                ">
                    🌱
                </div>

                <h1 style="
                    margin:0;
                    font-size:32px;
                ">
                    Agrivision
                </h1>

                <p style="
                    margin:10px 0 0;
                    font-size:14px;
                ">
                    Smart Farming. Better Decisions.
                </p>

            </div>


            <!-- SUCCESS CONTENT -->

            <div style="
                padding:45px 40px;
                text-align:center;
            ">

                <!-- SECURITY ICON -->

                <div style="
                    width:76px;
                    height:76px;
                    margin:0 auto 20px;
                    border-radius:50%;
                    background:#e8f5e9;
                    color:#2e7d32;
                    font-size:38px;
                    line-height:76px;
                ">
                    🔐
                </div>


                <h2 style="
                    color:#263238;
                    margin:0;
                    font-size:27px;
                ">
                    Password Changed Successfully
                </h2>


                <p style="
                    margin-top:20px;
                    color:#607d8b;
                    font-size:16px;
                    line-height:1.7;
                ">

                    Hello
                    <strong>
                        {user.first_name or user.username}
                    </strong>,

                </p>


                <p style="
                    color:#607d8b;
                    font-size:15px;
                    line-height:1.7;
                ">
                    Your Agrivision account password has been
                    successfully changed.
                </p>


                <!-- SUCCESS BOX -->

                <div style="
                    margin-top:30px;
                    padding:20px;
                    background:#e8f5e9;
                    border-radius:12px;
                    color:#2e7d32;
                    font-size:15px;
                    font-weight:bold;
                ">

                    ✓ Your account is secure

                </div>


                <p style="
                    margin-top:25px;
                    color:#90a4ae;
                    font-size:13px;
                    line-height:1.6;
                ">
                    If you did not make this password change,
                    please secure your account immediately.
                </p>

            </div>


            <!-- FOOTER -->

            <div style="
                padding:20px;
                text-align:center;
                background:#f5f7f5;
                color:#78909c;
                font-size:12px;
            ">

                © Agrivision — Analyze Soil. Grow Smarter.

            </div>

        </div>

    </body>

    </html>
    """

    return send_brevo_email(
        user=user,
        subject="Your Agrivision password was changed",
        html_content=html_content,
    )