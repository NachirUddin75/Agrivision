document.addEventListener("DOMContentLoaded", () => {

    const usernameForm =
        document.getElementById(
            "usernameForm"
        );

    const otpForm =
        document.getElementById(
            "otpForm"
        );

    const passwordForm =
        document.getElementById(
            "passwordForm"
        );


    const usernameInput =
        document.getElementById(
            "username"
        );

    const otpInput =
        document.getElementById(
            "otp"
        );

    const newPasswordInput =
        document.getElementById(
            "newPassword"
        );

    const confirmPasswordInput =
        document.getElementById(
            "confirmPassword"
        );


    const requestOtpButton =
        document.getElementById(
            "requestOtpButton"
        );

    const verifyOtpButton =
        document.getElementById(
            "verifyOtpButton"
        );

    const resetPasswordButton =
        document.getElementById(
            "resetPasswordButton"
        );


    const errorBox =
        document.getElementById(
            "forgotError"
        );

    const messageBox =
        document.getElementById(
            "forgotMessage"
        );


    const pageTitle =
        document.getElementById(
            "pageTitle"
        );

    const pageSubtitle =
        document.getElementById(
            "pageSubtitle"
        );


    const otpUsername =
        document.getElementById(
            "otpUsername"
        );


    let username = "";

    let otp = "";


    /* ==================================
       PASSWORD VISIBILITY
    ================================== */

    setupPasswordToggle(
        "newPasswordToggle",
        "newPassword"
    );

    setupPasswordToggle(
        "confirmPasswordToggle",
        "confirmPassword"
    );


    function setupPasswordToggle(
        buttonId,
        inputId
    ) {

        const button =
            document.getElementById(
                buttonId
            );

        const input =
            document.getElementById(
                inputId
            );


        button.addEventListener(
            "click",
            () => {

                if (
                    input.type ===
                    "password"
                ) {

                    input.type =
                        "text";

                    button.textContent =
                        "🙈";

                } else {

                    input.type =
                        "password";

                    button.textContent =
                        "👁️";

                }

            }
        );

    }


    /* ==================================
       OTP ONLY NUMBERS
    ================================== */

    otpInput.addEventListener(
        "input",
        () => {

            otpInput.value =
                otpInput.value
                    .replace(/\D/g, "")
                    .slice(0, 6);

            clearError();

            clearMessage();

        }
    );


    /* ==================================
       STEP 1
    ================================== */

    usernameForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            username =
                usernameInput.value.trim();


            if (!username) {

                showError(
                    "Please enter your username or email."
                );

                return;
            }


            setButtonLoading(
                requestOtpButton,
                true,
                "Sending OTP..."
            );

            clearMessages();


            try {

                const result =
                    await apiRequest(
                        "/accounts/forgot-password/request-otp/",
                        {
                            method: "POST",

                            body:
                                JSON.stringify({
                                    username:
                                        username,
                                }),
                        }
                    );


                if (!result.ok) {

                    showApiError(
                        result.data,
                        [
                            "username",
                            "non_field_errors",
                        ],
                        "Unable to send OTP. Please try again."
                    );

                    return;
                }


                showMessage(
                    result.data.message ||
                    "OTP sent successfully. Please check your email."
                );


                otpUsername.textContent =
                    username;


                usernameForm.classList.add(
                    "d-none"
                );

                otpForm.classList.remove(
                    "d-none"
                );


                pageTitle.textContent =
                    "Verify OTP";

                pageSubtitle.textContent =
                    "Enter the OTP sent to your email";

            } catch (error) {

                console.error(error);

                showError(
                    "Unable to send OTP. Please try again."
                );

            } finally {

                setButtonLoading(
                    requestOtpButton,
                    false,
                    "Send Reset OTP"
                );

            }

        }
    );


    /* ==================================
       STEP 2
    ================================== */

    otpForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            otp =
                otpInput.value.trim();


            if (!otp) {

                showError(
                    "Please enter the OTP."
                );

                return;
            }


            if (otp.length !== 6) {

                showError(
                    "OTP must contain 6 digits."
                );

                return;
            }


            setButtonLoading(
                verifyOtpButton,
                true,
                "Verifying..."
            );

            clearMessages();


            try {

                const result =
                    await apiRequest(
                        "/accounts/forgot-password/verify-otp/",
                        {
                            method: "POST",

                            body:
                                JSON.stringify({
                                    username:
                                        username,

                                    otp:
                                        otp,
                                }),
                        }
                    );


                if (!result.ok) {

                    showApiError(
                        result.data,
                        [
                            "username",
                            "otp",
                            "non_field_errors",
                        ],
                        "Invalid OTP. Please try again."
                    );

                    return;
                }


                showMessage(
                    result.data.message ||
                    "OTP verified successfully."
                );


                otpForm.classList.add(
                    "d-none"
                );

                passwordForm.classList.remove(
                    "d-none"
                );


                pageTitle.textContent =
                    "New Password";

                pageSubtitle.textContent =
                    "Create a new secure password";

            } catch (error) {

                console.error(error);

                showError(
                    "Invalid OTP. Please try again."
                );

            } finally {

                setButtonLoading(
                    verifyOtpButton,
                    false,
                    "Verify OTP"
                );

            }

        }
    );


    /* ==================================
       STEP 3
    ================================== */

    passwordForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            const newPassword =
                newPasswordInput.value;

            const confirmPassword =
                confirmPasswordInput.value;


            if (!newPassword) {

                showError(
                    "Please enter a new password."
                );

                return;
            }


            if (
                newPassword.length < 8
            ) {

                showError(
                    "Password must contain at least 8 characters."
                );

                return;
            }


            if (!confirmPassword) {

                showError(
                    "Please confirm your new password."
                );

                return;
            }


            if (
                newPassword !==
                confirmPassword
            ) {

                showError(
                    "Passwords do not match."
                );

                return;
            }


            setButtonLoading(
                resetPasswordButton,
                true,
                "Changing Password..."
            );

            clearMessages();


            try {

                const result =
                    await apiRequest(
                        "/accounts/forgot-password/reset/",
                        {
                            method: "POST",

                            body:
                                JSON.stringify({
                                    username:
                                        username,

                                    otp:
                                        otp,

                                    new_password:
                                        newPassword,

                                    confirm_password:
                                        confirmPassword,
                                }),
                        }
                    );


                if (!result.ok) {

                    showApiError(
                        result.data,
                        [
                            "username",
                            "otp",
                            "new_password",
                            "confirm_password",
                            "non_field_errors",
                        ],
                        "Unable to change password. Please try again."
                    );

                    return;
                }


                showMessage(
                    result.data.message ||
                    "Password changed successfully."
                );


                /*
                 * Same delay as React:
                 * 1200 milliseconds.
                 */

                setTimeout(() => {

                    window.location.href =
                        "login.html";

                }, 1200);

            } catch (error) {

                console.error(error);

                showError(
                    "Unable to change password. Please try again."
                );

            } finally {

                setButtonLoading(
                    resetPasswordButton,
                    false,
                    "Change Password"
                );

            }

        }
    );


    /* ==================================
       BACK TO USERNAME
    ================================== */

    document
        .getElementById(
            "backToUsernameButton"
        )
        .addEventListener(
            "click",
            () => {

                username = "";

                otp = "";

                usernameInput.value =
                    "";

                otpInput.value =
                    "";

                newPasswordInput.value =
                    "";

                confirmPasswordInput.value =
                    "";

                otpForm.classList.add(
                    "d-none"
                );

                passwordForm.classList.add(
                    "d-none"
                );

                usernameForm.classList.remove(
                    "d-none"
                );


                pageTitle.textContent =
                    "Forgot Password";

                pageSubtitle.textContent =
                    "Reset your Agrivision account password";

                clearMessages();

            }
        );


    /* ==================================
       BACK TO OTP
    ================================== */

    document
        .getElementById(
            "backToOtpButton"
        )
        .addEventListener(
            "click",
            () => {

                newPasswordInput.value =
                    "";

                confirmPasswordInput.value =
                    "";

                passwordForm.classList.add(
                    "d-none"
                );

                otpForm.classList.remove(
                    "d-none"
                );


                pageTitle.textContent =
                    "Verify OTP";

                pageSubtitle.textContent =
                    "Enter the OTP sent to your email";

                clearMessages();

            }
        );


    /* ==================================
       HELPERS
    ================================== */

    function showError(message) {

        errorBox.textContent =
            message;

        errorBox.classList.remove(
            "d-none"
        );

    }


    function showMessage(message) {

        messageBox.textContent =
            message;

        messageBox.classList.remove(
            "d-none"
        );

    }


    function clearError() {

        errorBox.textContent =
            "";

        errorBox.classList.add(
            "d-none"
        );

    }


    function clearMessage() {

        messageBox.textContent =
            "";

        messageBox.classList.add(
            "d-none"
        );

    }


    function clearMessages() {

        clearError();

        clearMessage();

    }


    function showApiError(
        data,
        fields,
        fallback
    ) {

        for (
            const field of fields
        ) {

            if (
                data?.[field]
            ) {

                const value =
                    data[field];

                if (
                    Array.isArray(
                        value
                    )
                ) {

                    showError(
                        value[0]
                    );

                } else {

                    showError(
                        value
                    );
                }

                return;
            }

        }


        showError(
            data?.message ||
            fallback
        );

    }


    function setButtonLoading(
        button,
        loading,
        loadingText
    ) {

        if (loading) {

            button.disabled =
                true;

            button.textContent =
                loadingText;

        } else {

            button.disabled =
                false;

            if (
                button ===
                requestOtpButton
            ) {

                button.textContent =
                    "Send Reset OTP";

            } else if (
                button ===
                verifyOtpButton
            ) {

                button.textContent =
                    "Verify OTP";

            } else {

                button.textContent =
                    "Change Password";

            }

        }

    }

});