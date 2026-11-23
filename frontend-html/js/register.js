document.addEventListener("DOMContentLoaded", () => {

    const form =
        document.getElementById("registerForm");

    const usernameInput =
        document.getElementById("username");

    const usernameIcon =
        document.getElementById(
            "usernameStatusIcon"
        );

    const usernameMessage =
        document.getElementById(
            "usernameStatusMessage"
        );

    const passwordInput =
        document.getElementById("password");

    const confirmPasswordInput =
        document.getElementById(
            "confirm_password"
        );

    const passwordToggle =
        document.getElementById(
            "passwordToggle"
        );

    const confirmPasswordToggle =
        document.getElementById(
            "confirmPasswordToggle"
        );

    const registerButton =
        document.getElementById(
            "registerButton"
        );

    const errorBox =
        document.getElementById(
            "registerError"
        );


    let usernameStatus = {
        checking: false,
        available: null,
        message: "",
    };


    let usernameTimer = null;


    /* ==========================
       PASSWORD TOGGLES
    ========================== */

    passwordToggle.addEventListener(
        "click",
        () => {

            if (
                passwordInput.type ===
                "password"
            ) {

                passwordInput.type = "text";

                passwordToggle.textContent =
                    "🙈";

            } else {

                passwordInput.type =
                    "password";

                passwordToggle.textContent =
                    "👁️";

            }

        }
    );


    confirmPasswordToggle.addEventListener(
        "click",
        () => {

            if (
                confirmPasswordInput.type ===
                "password"
            ) {

                confirmPasswordInput.type =
                    "text";

                confirmPasswordToggle.textContent =
                    "🙈";

            } else {

                confirmPasswordInput.type =
                    "password";

                confirmPasswordToggle.textContent =
                    "👁️";

            }

        }
    );


    /* ==========================
       USERNAME CHECK
    ========================== */

    usernameInput.addEventListener(
        "input",
        () => {

            clearError();

            clearTimeout(
                usernameTimer
            );


            const username =
                usernameInput.value.trim();


            if (!username) {

                setUsernameStatus(
                    false,
                    null,
                    ""
                );

                return;
            }


            if (username.length < 3) {

                setUsernameStatus(
                    false,
                    false,
                    "Username must contain at least 3 characters."
                );

                return;
            }


            setUsernameStatus(
                true,
                null,
                ""
            );


            /*
             * Same 500ms delay
             * used by React.
             */

            usernameTimer =
                setTimeout(
                    () => checkUsername(username),
                    500
                );

        }
    );


    async function checkUsername(
        username
    ) {

        try {

            const result =
                await apiRequest(
                    `/accounts/check-username/?username=${encodeURIComponent(username)}`,
                    {
                        method: "GET",
                    }
                );


            if (!result.ok) {

                setUsernameStatus(
                    false,
                    null,
                    "Unable to check username."
                );

                return;
            }


            setUsernameStatus(
                false,
                result.data.available,
                result.data.message
            );

        } catch (error) {

            setUsernameStatus(
                false,
                null,
                "Unable to check username."
            );

        }

    }


    function setUsernameStatus(
        checking,
        available,
        message
    ) {

        usernameStatus = {
            checking,
            available,
            message,
        };


        usernameIcon.innerHTML =
            "";

        usernameMessage.textContent =
            message;


        usernameMessage.className =
            "username-message";


        if (checking) {

            const spinner =
                document.createElement(
                    "div"
                );

            spinner.className =
                "agr-spinner";

            usernameIcon.appendChild(
                spinner
            );

            usernameMessage.classList.add(
                "checking"
            );

            return;
        }


        if (
            available === true
        ) {

            usernameIcon.textContent =
                "✓";

            usernameIcon.classList.add(
                "username-available"
            );

            usernameMessage.classList.add(
                "available"
            );

            return;
        }


        if (
            available === false
        ) {

            usernameIcon.textContent =
                "×";

            usernameIcon.classList.add(
                "username-unavailable"
            );

            usernameMessage.classList.add(
                "unavailable"
            );

        }

    }


    /* ==========================
       SUBMIT
    ========================== */

    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            clearError();


            const username =
                usernameInput.value.trim();

            const firstName =
                document.getElementById(
                    "first_name"
                ).value.trim();

            const lastName =
                document.getElementById(
                    "last_name"
                ).value.trim();

            const email =
                document.getElementById(
                    "email"
                ).value.trim();

            const password =
                passwordInput.value;

            const confirmPassword =
                confirmPasswordInput.value;


            /*
             * Same validation
             * as Register.jsx
             */

            if (
                !username ||
                !firstName ||
                !email ||
                !password
            ) {

                showError(
                    "Please fill in all required fields."
                );

                return;
            }


            if (
                usernameStatus.available ===
                false
            ) {

                showError(
                    "Please choose another username."
                );

                return;
            }


            if (
                usernameStatus.checking
            ) {

                showError(
                    "Please wait while we check your username."
                );

                return;
            }


            if (
                password.length < 8
            ) {

                showError(
                    "Password must contain at least 8 characters."
                );

                return;
            }


            if (
                password !==
                confirmPassword
            ) {

                showError(
                    "Passwords do not match."
                );

                return;
            }


            registerButton.disabled =
                true;

            registerButton.textContent =
                "Creating Account...";


            try {

                const result =
                    await apiRequest(
                        "/accounts/register/",
                        {
                            method: "POST",

                            body:
                                JSON.stringify({
                                    username:
                                        username,

                                    first_name:
                                        firstName,

                                    last_name:
                                        lastName,

                                    email:
                                        email,

                                    password:
                                        password,
                                }),
                        }
                    );


                if (!result.ok) {

                    const data =
                        result.data;


                    if (data?.email) {

                        showError(
                            data.email[0]
                        );

                    } else if (
                        data?.username
                    ) {

                        showError(
                            data.username[0]
                        );

                    } else if (
                        data?.password
                    ) {

                        showError(
                            data.password[0]
                        );

                    } else {

                        showError(
                            data?.message ||
                            "Registration failed. Please try again."
                        );
                    }

                    return;
                }


                /*
                 * Same React navigation:
                 *
                 * navigate(
                 *   "/registration-success"
                 * )
                 */

                window.location.href =
                    "registration-success.html";

            } catch (error) {

                console.error(error);

                showError(
                    "Registration failed. Please try again."
                );

            } finally {

                registerButton.disabled =
                    false;

                registerButton.textContent =
                    "Create Account";

            }

        }
    );


    function showError(message) {

        errorBox.textContent =
            message;

        errorBox.classList.remove(
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

});