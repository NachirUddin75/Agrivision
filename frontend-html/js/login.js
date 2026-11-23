document.addEventListener("DOMContentLoaded", function () {

    console.log("Login JavaScript loaded");


    const form =
        document.getElementById("login-form");

    const usernameInput =
        document.getElementById("username");

    const passwordInput =
        document.getElementById("password");

    const errorMessage =
        document.getElementById("error-message");

    const successMessage =
        document.getElementById("success-message");

    const loginButton =
        document.getElementById("login-button");

    const loginButtonText =
        document.getElementById("login-button-text");

    const loginSpinner =
        document.getElementById("login-spinner");

    const togglePassword =
        document.getElementById("toggle-password");


    /*
     * Check required elements
     */

    if (!form) {
        console.error("login-form not found");
        return;
    }

    if (!usernameInput) {
        console.error("username input not found");
        return;
    }

    if (!passwordInput) {
        console.error("password input not found");
        return;
    }

    if (!loginButton) {
        console.error("login button not found");
        return;
    }


    /*
     * Hide messages
     */

    function hideMessages() {

        errorMessage.classList.add("d-none");
        successMessage.classList.add("d-none");

        errorMessage.textContent = "";
        successMessage.textContent = "";
    }


    /*
     * Show error
     */

    function showError(message) {

        successMessage.classList.add("d-none");

        errorMessage.textContent =
            message;

        errorMessage.classList.remove(
            "d-none"
        );
    }


    /*
     * Show success
     */

    function showSuccess(message) {

        errorMessage.classList.add("d-none");

        successMessage.textContent =
            message;

        successMessage.classList.remove(
            "d-none"
        );
    }


    /*
     * Loading
     */

    function setLoading(isLoading) {

        loginButton.disabled =
            isLoading;


        if (isLoading) {

            loginButtonText.textContent =
                "Logging in...";

            loginSpinner.classList.remove(
                "d-none"
            );

        } else {

            loginButtonText.textContent =
                "Login";

            loginSpinner.classList.add(
                "d-none"
            );
        }
    }



    /*
     * Show / hide password
     */

    if (togglePassword) {

        togglePassword.addEventListener(
            "click",
            function () {

                if (
                    passwordInput.type === "password"
                ) {

                    passwordInput.type =
                        "text";

                    togglePassword.textContent =
                        "🙈";

                    togglePassword.setAttribute(
                        "aria-label",
                        "Hide password"
                    );

                } else {

                    passwordInput.type =
                        "password";

                    togglePassword.textContent =
                        "👁️";

                    togglePassword.setAttribute(
                        "aria-label",
                        "Show password"
                    );
                }

            }
        );
    }



    /*
     * LOGIN
     */

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            console.log(
                "Login form submitted"
            );


            hideMessages();


            const username =
                usernameInput.value.trim();

            const password =
                passwordInput.value;


            /*
             * Validation
             */

            if (!username) {

                showError(
                    "Please enter your username or email."
                );

                usernameInput.focus();

                return;
            }


            if (!password) {

                showError(
                    "Please enter your password."
                );

                passwordInput.focus();

                return;
            }


            setLoading(true);


            try {

                console.log(
                    "Sending request to Django..."
                );


                /*
                 * Existing backend endpoint
                 *
                 * http://127.0.0.1:8000/api/accounts/login/
                 */

                const response =
                    await apiRequest(
                        "/accounts/login/",
                        {
                            method: "POST",

                            body: JSON.stringify({
                                username:
                                    username,

                                password:
                                    password,
                            }),
                        }
                    );


                console.log(
                    "Django response:",
                    response
                );


                /*
                 * Login failed
                 */

                if (!response.ok) {

                    let message =
                        "Login failed.";


                    if (
                        response.data &&
                        response.data.message
                    ) {

                        message =
                            response.data.message;

                    } else if (
                        response.data &&
                        response.data.detail
                    ) {

                        message =
                            response.data.detail;

                    } else if (
                        response.data &&
                        response.data.error
                    ) {

                        message =
                            response.data.error;

                    } else if (
                        response.data &&
                        typeof response.data === "object"
                    ) {

                        const values =
                            Object.values(
                                response.data
                            );


                        if (
                            values.length > 0
                        ) {

                            const first =
                                values[0];


                            if (
                                Array.isArray(
                                    first
                                )
                            ) {

                                message =
                                    first[0];

                            } else {

                                message =
                                    String(first);
                            }
                        }
                    }


                    showError(message);

                    return;
                }



                /*
                 * SUCCESS
                 */

                console.log(
                    "Login successful"
                );


                /*
                 * Save:
                 *
                 * access_token
                 * refresh_token
                 * user
                 */

                saveAuthData(
                    response.data
                );


                showSuccess(
                    "Login successful. Redirecting..."
                );


                /*
                 * Go to dashboard
                 */

                setTimeout(
                    function () {

                        window.location.href =
                            "dashboard.html";

                    },
                    500
                );

            } catch (error) {

                console.error(
                    "Login request error:",
                    error
                );


                showError(
                    "Unable to connect to Agrivision server."
                );

            } finally {

                setLoading(false);
            }

        }
    );


});