document.addEventListener(
    "DOMContentLoaded",
    async () => {

        const params =
            new URLSearchParams(
                window.location.search
            );

        const token =
            params.get("token");


        const verifyingState =
            document.getElementById(
                "verifyingState"
            );

        const successState =
            document.getElementById(
                "successState"
            );

        const errorState =
            document.getElementById(
                "errorState"
            );

        const successMessage =
            document.getElementById(
                "successMessage"
            );

        const errorMessage =
            document.getElementById(
                "errorMessage"
            );


        /*
         * Same validation as React
         */

        if (!token) {

            verifyingState.classList.add(
                "d-none"
            );

            errorState.classList.remove(
                "d-none"
            );

            errorMessage.textContent =
                "Verification token is missing.";

            return;
        }


        try {

            const result =
                await apiRequest(
                    "/accounts/verify-email/",
                    {
                        method: "POST",

                        body:
                            JSON.stringify({
                                token: token,
                            }),
                    }
                );


            if (result.ok) {

                verifyingState.classList.add(
                    "d-none"
                );

                successState.classList.remove(
                    "d-none"
                );


                successMessage.textContent =
                    result.data.message ||
                    "Your email has been verified successfully.";

            } else {

                verifyingState.classList.add(
                    "d-none"
                );

                errorState.classList.remove(
                    "d-none"
                );


                errorMessage.textContent =
                    result.data.message ||
                    "Unable to verify your email. The link may be invalid or expired.";
            }

        } catch (error) {

            verifyingState.classList.add(
                "d-none"
            );

            errorState.classList.remove(
                "d-none"
            );

            errorMessage.textContent =
                "Unable to verify your email. The link may be invalid or expired.";

        }

    }
);