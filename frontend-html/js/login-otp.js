document.addEventListener("DOMContentLoaded", () => {

    const usernameForm =
        document.getElementById("usernameForm");

    const otpForm =
        document.getElementById("otpForm");

    const usernameInput =
        document.getElementById("username");

    const otpInput =
        document.getElementById("otp");

    const otpUsername =
        document.getElementById("otpUsername");

    const sendOtpButton =
        document.getElementById("sendOtpButton");

    const verifyOtpButton =
        document.getElementById("verifyOtpButton");

    const changeUsernameButton =
        document.getElementById(
            "changeUsernameButton"
        );

    const errorBox =
        document.getElementById("otpError");

    const messageBox =
        document.getElementById("otpMessage");

    const pageTitle =
        document.getElementById("pageTitle");

    const pageSubtitle =
        document.getElementById(
            "pageSubtitle"
        );


    let username = "";


    /* ==========================
       STEP 1
    ========================== */

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


            setLoading(
                sendOtpButton,
                true,
                "Sending OTP..."
            );

            clearMessages();


            try {

                const result =
                    await apiRequest(
                        "/accounts/request-otp/",
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

                    const data =
                        result.data;


                    if (
                        data?.username
                    ) {

                        showError(
                            data.username[0]
                        );

                    } else {

                        showError(
                            data?.message ||
                            "Unable to send OTP. Please try again."
                        );
                    }

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

                setLoading(
                    sendOtpButton,
                    false,
                    "Send OTP"
                );

            }

        }
    );


    /* ==========================
       OTP INPUT
    ========================== */

    otpInput.addEventListener(
        "input",
        () => {

            otpInput.value =
                otpInput.value
                    .replace(/\D/g, "")
                    .slice(0, 6);

            clearError();

        }
    );


    /* ==========================
       STEP 2
    ========================== */

    otpForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            const otp =
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


            setLoading(
                verifyOtpButton,
                true,
                "Verifying..."
            );

            clearMessages();


            try {

                const result =
                    await apiRequest(
                        "/accounts/verify-otp/",
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

                    const data =
                        result.data;


                    if (
                        data?.username
                    ) {

                        showError(
                            data.username[0]
                        );

                    } else if (
                        data?.otp
                    ) {

                        showError(
                            data.otp[0]
                        );

                    } else {

                        showError(
                            data?.message ||
                            "Invalid OTP. Please try again."
                        );
                    }

                    return;
                }


                /*
                 * EXACT SAME JWT STORAGE
                 * used by React.
                 */

                localStorage.setItem(
                    "access_token",
                    result.data.access
                );

                localStorage.setItem(
                    "refresh_token",
                    result.data.refresh
                );

                localStorage.setItem(
                    "user",
                    JSON.stringify(
                        result.data.user
                    )
                );


                showMessage(
                    result.data.message ||
                    "OTP login successful."
                );


                /*
                 * React used:
                 *
                 * setTimeout(() => {
                 *     navigate("/dashboard");
                 * }, 500)
                 */

                setTimeout(() => {

                    window.location.href =
                        "dashboard.html";

                }, 500);

            } catch (error) {

                console.error(error);

                showError(
                    "Invalid OTP. Please try again."
                );

            } finally {

                setLoading(
                    verifyOtpButton,
                    false,
                    "Verify OTP"
                );

            }

        }
    );


    /* ==========================
       CHANGE USERNAME
    ========================== */

    changeUsernameButton.addEventListener(
        "click",
        () => {

            username = "";

            otpInput.value = "";

            usernameInput.value = "";

            usernameForm.classList.remove(
                "d-none"
            );

            otpForm.classList.add(
                "d-none"
            );

            pageTitle.textContent =
                "OTP Login";

            pageSubtitle.textContent =
                "Login securely using a one-time password";

            clearMessages();

        }
    );


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

        errorBox.textContent = "";

        errorBox.classList.add(
            "d-none"
        );

    }


    function clearMessages() {

        clearError();

        messageBox.textContent = "";

        messageBox.classList.add(
            "d-none"
        );

    }


    function setLoading(
        button,
        loading,
        loadingText
    ) {

        button.disabled =
            loading;

        button.textContent =
            loading
                ? loadingText
                : (
                    button === sendOtpButton
                        ? "Send OTP"
                        : "Verify OTP"
                );

    }

});