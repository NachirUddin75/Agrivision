document.addEventListener("DOMContentLoaded", function () {

    const successBox =
        document.getElementById("support-success");

    const errorBox =
        document.getElementById("support-error");

    const loadingBox =
        document.getElementById("support-loading");

    const emptyBox =
        document.getElementById("support-empty");

    const supportList =
        document.getElementById("support-list");

    const supportForm =
        document.getElementById("support-form");

    const subjectInput =
        document.getElementById("support-subject");

    const messageInput =
        document.getElementById("support-message");

    const submitButton =
        document.getElementById("support-submit-button");

    const submitText =
        document.getElementById("support-submit-text");

    const submitSpinner =
        document.getElementById("support-submit-spinner");


    let supports = [];

    const replyMessages = {};

    let replyingId = null;


    /*
     * =========================================================
     * AUTHENTICATION
     * =========================================================
     */

    function getAccessToken() {

        return localStorage.getItem(
            "access_token"
        );
    }


    function getAuthHeaders() {

        const accessToken =
            getAccessToken();

        if (!accessToken) {
            return null;
        }

        return {
            Authorization:
                `Bearer ${accessToken}`,
        };
    }


    /*
     * =========================================================
     * MESSAGES
     * =========================================================
     */

    function clearMessages() {

        successBox.classList.add("d-none");
        errorBox.classList.add("d-none");

        successBox.textContent = "";
        errorBox.textContent = "";
    }


    function showSuccess(message) {

        successBox.textContent = message;

        successBox.classList.remove("d-none");

        errorBox.classList.add("d-none");
    }


    function showError(message) {

        errorBox.textContent = message;

        errorBox.classList.remove("d-none");

        successBox.classList.add("d-none");
    }


    /*
     * =========================================================
     * UNAUTHORIZED
     * =========================================================
     */

    function handleUnauthorized() {

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "refresh_token"
        );

        localStorage.removeItem(
            "user"
        );

        showError(
            "Your login session has expired. Please login again."
        );

        setTimeout(function () {

            window.location.href =
                "login.html";

        }, 1000);
    }


    /*
     * =========================================================
     * STATUS STYLE
     * =========================================================
     */

    function getStatusClass(status) {

        switch (status) {

            case "open":
                return "status-open";

            case "in_progress":
                return "status-in-progress";

            case "replied":
                return "status-replied";

            case "resolved":
                return "status-resolved";

            case "closed":
                return "status-closed";

            default:
                return "status-closed";
        }
    }


    /*
     * =========================================================
     * FETCH SUPPORT REQUESTS
     * =========================================================
     */

    async function fetchSupportRequests() {

        try {

            loadingBox.classList.remove(
                "d-none"
            );

            emptyBox.classList.add(
                "d-none"
            );

            supportList.classList.add(
                "d-none"
            );

            clearMessages();


            const headers =
                getAuthHeaders();

            if (!headers) {

                handleUnauthorized();

                return;
            }


            const response =
                await apiRequest(
                    "/support/",
                    {
                        method: "GET",
                        headers,
                    }
                );


            if (!response.ok) {

                if (response.status === 401) {

                    handleUnauthorized();

                    return;
                }

                showError(
                    response.data?.message ||
                    response.data?.detail ||
                    "Unable to load your support history. Please try again."
                );

                return;
            }


            supports =
                Array.isArray(response.data)
                    ? response.data
                    : [];


            renderSupportRequests();

        } catch (error) {

            console.error(
                "Support history error:",
                error
            );

            showError(
                "Unable to load your support history. Please try again."
            );

        } finally {

            loadingBox.classList.add(
                "d-none"
            );
        }
    }


    /*
     * =========================================================
     * RENDER SUPPORT REQUESTS
     * =========================================================
     */

    function renderSupportRequests() {

        supportList.innerHTML = "";


        if (supports.length === 0) {

            emptyBox.classList.remove(
                "d-none"
            );

            return;
        }


        supportList.classList.remove(
            "d-none"
        );


        supports.forEach(function (support) {

            supportList.appendChild(
                createSupportCard(support)
            );

        });
    }


    /*
     * =========================================================
     * SUPPORT CARD
     * =========================================================
     */

    function createSupportCard(support) {

        const card =
            document.createElement("div");

        card.className =
            "support-card bg-white border rounded-4 shadow-sm p-4";


        const statusClass =
            getStatusClass(
                support.status
            );


        card.innerHTML = `

            <div class="d-flex justify-content-between align-items-start gap-3">

                <div class="flex-grow-1">

                    <p class="text-uppercase small fw-bold text-secondary mb-2">
                        Ticket #${escapeHtml(support.id)}
                    </p>

                    <h3 class="h5 fw-bold text-dark mb-1">
                        ${escapeHtml(support.subject)}
                    </h3>

                    <p class="small text-secondary mb-0">
                        Submitted
                        ${formatDate(support.created_at)}
                    </p>

                </div>

                <span class="status-badge ${statusClass}">
                    ${escapeHtml(support.status_display || support.status)}
                </span>

            </div>


            <!-- Original Problem -->

            <div class="problem-box mt-4">

                <p class="text-uppercase small fw-bold text-secondary mb-2">
                    Your Problem
                </p>

                <p class="small text-dark lh-lg mb-0 preserve-whitespace">
                    ${escapeHtml(support.message)}
                </p>

            </div>


            ${renderConversation(support)}


            ${renderOldAdminReply(support)}


            ${renderReplyBox(support)}


            ${renderClosedMessage(support)}


            <div class="text-end mt-4">

                <p class="small text-secondary mb-0">
                    Last updated
                    ${formatDate(support.updated_at)}
                </p>

            </div>

        `;


        attachReplyEvents(
            card,
            support
        );


        return card;
    }


    /*
     * =========================================================
     * CONVERSATION
     * =========================================================
     */

    function renderConversation(support) {

        if (
            !support.replies ||
            support.replies.length === 0
        ) {
            return "";
        }


        let html = `

            <div class="mt-4">

                <p class="text-uppercase small fw-bold text-secondary mb-3">
                    Conversation
                </p>

                <div class="d-flex flex-column gap-3">

        `;


        support.replies.forEach(function (reply) {

            const adminClass =
                reply.is_admin
                    ? "admin-reply"
                    : "user-reply";


            const senderClass =
                reply.is_admin
                    ? "text-success"
                    : "text-primary";


            html += `

                <div class="reply-box ${adminClass}">

                    <div class="d-flex justify-content-between align-items-center gap-3">

                        <p class="small fw-bold text-uppercase ${senderClass} mb-0">
                            ${escapeHtml(reply.sender)}
                        </p>

                        <p class="small text-secondary mb-0">
                            ${formatDate(reply.created_at)}
                        </p>

                    </div>

                    <p class="small text-dark lh-lg mt-2 mb-0 preserve-whitespace">
                        ${escapeHtml(reply.message)}
                    </p>

                </div>

            `;
        });


        html += `

                </div>

            </div>

        `;


        return html;
    }


    /*
     * =========================================================
     * OLD ADMIN REPLY COMPATIBILITY
     * =========================================================
     */

    function renderOldAdminReply(support) {

        if (
            support.admin_reply &&
            (
                !support.replies ||
                support.replies.length === 0
            )
        ) {

            return `

                <div class="reply-box admin-reply mt-3">

                    <p class="text-uppercase small fw-bold text-success mb-2">
                        Admin Reply
                    </p>

                    <p class="small text-dark lh-lg mb-0 preserve-whitespace">
                        ${escapeHtml(support.admin_reply)}
                    </p>

                </div>

            `;
        }


        return "";
    }


    /*
     * =========================================================
     * REPLY BOX
     * =========================================================
     */

    function renderReplyBox(support) {

        if (
            support.status === "closed"
        ) {
            return "";
        }


        const currentMessage =
            replyMessages[support.id] || "";


        return `

            <div class="reply-form-box mt-4">

                <p class="text-uppercase small fw-bold text-secondary mb-2">
                    Reply to Admin
                </p>

                <textarea
                    class="form-control bg-light reply-input"
                    data-support-id="${support.id}"
                    rows="3"
                    placeholder="Write your reply to the support team..."
                >${escapeHtml(currentMessage)}</textarea>

                <div class="text-end mt-3">

                    <button
                        type="button"
                        class="btn btn-success fw-semibold send-reply-button"
                        data-support-id="${support.id}"
                    >
                        <span class="reply-button-text">
                            Send Reply
                        </span>

                        <span
                            class="spinner-border spinner-border-sm reply-spinner d-none"
                            role="status"
                        ></span>

                    </button>

                </div>

            </div>

        `;
    }


    /*
     * =========================================================
     * CLOSED MESSAGE
     * =========================================================
     */

    function renderClosedMessage(support) {

        if (
            support.status !== "closed"
        ) {
            return "";
        }


        return `

            <div class="alert alert-secondary mt-4 mb-0 small">

                This support request is closed.
                You cannot send additional replies.

            </div>

        `;
    }


    /*
     * =========================================================
     * REPLY EVENTS
     * =========================================================
     */

    function attachReplyEvents(card, support) {

        const replyInput =
            card.querySelector(
                `.reply-input[data-support-id="${support.id}"]`
            );


        if (replyInput) {

            replyInput.addEventListener(
                "input",
                function () {

                    replyMessages[support.id] =
                        replyInput.value;

                    clearMessages();
                }
            );
        }


        const replyButton =
            card.querySelector(
                `.send-reply-button[data-support-id="${support.id}"]`
            );


        if (replyButton) {

            replyButton.addEventListener(
                "click",
                function () {

                    handleReplySubmit(
                        support.id,
                        card
                    );

                }
            );
        }
    }


    /*
     * =========================================================
     * CREATE SUPPORT REQUEST
     * =========================================================
     */

    supportForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            clearMessages();


            const subject =
                subjectInput.value.trim();

            const message =
                messageInput.value.trim();


            if (!subject) {

                showError(
                    "Please enter a subject."
                );

                return;
            }


            if (!message) {

                showError(
                    "Please describe your problem."
                );

                return;
            }


            try {

                setSubmitting(true);


                const headers =
                    getAuthHeaders();

                if (!headers) {

                    handleUnauthorized();

                    return;
                }


                const response =
                    await apiRequest(
                        "/support/",
                        {
                            method: "POST",

                            headers,

                            body: JSON.stringify({
                                subject,
                                message,
                            }),
                        }
                    );


                if (!response.ok) {

                    if (response.status === 401) {

                        handleUnauthorized();

                        return;
                    }


                    showError(
                        response.data?.message ||
                        response.data?.detail ||
                        "Unable to submit your support request. Please try again."
                    );

                    return;
                }


                subjectInput.value = "";
                messageInput.value = "";


                showSuccess(
                    "Your support request has been submitted successfully."
                );


                await fetchSupportRequests();

            } catch (error) {

                console.error(
                    "Support submission error:",
                    error
                );

                showError(
                    "Unable to submit your support request. Please try again."
                );

            } finally {

                setSubmitting(false);
            }
        }
    );


    /*
     * =========================================================
     * SEND REPLY
     * =========================================================
     */

    async function handleReplySubmit(
        supportId,
        card
    ) {

        const input =
            card.querySelector(
                `.reply-input[data-support-id="${supportId}"]`
            );


        const button =
            card.querySelector(
                `.send-reply-button[data-support-id="${supportId}"]`
            );


        const buttonText =
            button.querySelector(
                ".reply-button-text"
            );


        const spinner =
            button.querySelector(
                ".reply-spinner"
            );


        const message =
            input.value.trim();


        if (!message) {

            showError(
                "Please enter a reply message."
            );

            return;
        }


        try {

            replyingId =
                supportId;

            clearMessages();


            button.disabled =
                true;

            buttonText.textContent =
                "Sending...";

            spinner.classList.remove(
                "d-none"
            );


            const headers =
                getAuthHeaders();

            if (!headers) {

                handleUnauthorized();

                return;
            }


            const response =
                await apiRequest(
                    `/support/${supportId}/reply/`,
                    {
                        method: "POST",

                        headers,

                        body: JSON.stringify({
                            message,
                        }),
                    }
                );


            if (!response.ok) {

                if (response.status === 401) {

                    handleUnauthorized();

                    return;
                }


                showError(
                    response.data?.message ||
                    response.data?.detail ||
                    "Unable to send your reply. Please try again."
                );

                return;
            }


            replyMessages[supportId] =
                "";


            showSuccess(
                "Your reply has been sent successfully."
            );


            await fetchSupportRequests();

        } catch (error) {

            console.error(
                "Support reply error:",
                error
            );

            showError(
                "Unable to send your reply. Please try again."
            );

        } finally {

            replyingId =
                null;

            button.disabled =
                false;

            buttonText.textContent =
                "Send Reply";

            spinner.classList.add(
                "d-none"
            );
        }
    }


    /*
     * =========================================================
     * SUBMIT LOADING
     * =========================================================
     */

    function setSubmitting(loading) {

        submitButton.disabled =
            loading;


        if (loading) {

            submitText.textContent =
                "Submitting...";

            submitSpinner.classList.remove(
                "d-none"
            );

        } else {

            submitText.textContent =
                "Submit Support Request";

            submitSpinner.classList.add(
                "d-none"
            );
        }
    }


    /*
     * =========================================================
     * DATE FORMAT
     * =========================================================
     */

    function formatDate(dateValue) {

        if (!dateValue) {
            return "";
        }


        const date =
            new Date(dateValue);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return "";
        }


        return date.toLocaleString();
    }


    /*
     * =========================================================
     * HTML ESCAPE
     * =========================================================
     */

    function escapeHtml(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }


        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    /*
     * =========================================================
     * INITIAL LOAD
     * =========================================================
     */

    fetchSupportRequests();

});