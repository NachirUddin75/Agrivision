from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import SupportRequest, SupportReply


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "subject",
        "user",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "subject",
        "message",
        "admin_reply",
        "user__username",
        "user__email",
        "replies__message",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "user",
        "subject",
        "message",
        "conversation",
        "admin_reply_box",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Support Request",
            {
                "fields": (
                    "user",
                    "subject",
                    "message",
                )
            },
        ),

        (
            "Conversation",
            {
                "fields": (
                    "conversation",
                )
            },
        ),

        (
            "Admin Reply",
            {
                "fields": (
                    "admin_reply_box",
                )
            },
        ),

        (
            "Status",
            {
                "fields": (
                    "status",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    list_per_page = 20

    # ==================================================
    # CUSTOM ADMIN URLS
    # ==================================================

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:object_id>/send-reply/",
                self.admin_site.admin_view(
                    self.send_admin_reply
                ),
                name="support_supportrequest_send_reply",
            ),
        ]

        return custom_urls + urls

    # ==================================================
    # NORMAL ADMIN SAVE
    # ==================================================

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context,
        )

    # ==================================================
    # SEND ADMIN REPLY
    # ==================================================

    def send_admin_reply(
        self,
        request,
        object_id,
    ):

        if request.method != "POST":

            return HttpResponseRedirect(
                reverse(
                    "admin:support_supportrequest_change",
                    args=[object_id],
                )
            )

        try:

            support_request = (
                SupportRequest.objects.get(
                    pk=object_id
                )
            )

        except SupportRequest.DoesNotExist:

            self.message_user(
                request,
                "Support request not found.",
                level=messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:support_supportrequest_changelist"
                )
            )

        message = request.POST.get(
            "admin_message",
            "",
        ).strip()

        if not message:

            self.message_user(
                request,
                "Reply message cannot be empty.",
                level=messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:support_supportrequest_change",
                    args=[object_id],
                )
            )

        # ----------------------------------------------
        # CREATE ADMIN REPLY
        # ----------------------------------------------

        SupportReply.objects.create(
            support_request=support_request,
            user=request.user,
            message=message,
            is_admin=True,
        )

        # ----------------------------------------------
        # UPDATE OLD ADMIN REPLY FIELD
        # ----------------------------------------------

        support_request.admin_reply = message

        # ----------------------------------------------
        # UPDATE STATUS
        # ----------------------------------------------

        support_request.status = "replied"

        support_request.save(
            update_fields=[
                "admin_reply",
                "status",
                "updated_at",
            ]
        )

        self.message_user(
            request,
            "Admin reply sent successfully.",
            level=messages.SUCCESS,
        )

        return HttpResponseRedirect(
            reverse(
                "admin:support_supportrequest_change",
                args=[object_id],
            )
        )

    # ==================================================
    # FORMAT DATETIME
    # ==================================================

    def format_datetime(self, value):

        if not value:
            return ""

        # Convert UTC datetime to Django's active local timezone.
        local_datetime = timezone.localtime(value)

        return local_datetime.strftime(
            "%d %b %Y, %I:%M %p"
        )

    # ==================================================
    # CONVERSATION
    # ==================================================

    @admin.display(
        description="Conversation"
    )
    def conversation(self, obj):

        replies = (
            obj.replies
            .select_related("user")
            .order_by("created_at")
        )

        html = """
        <div style="
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        ">
        """

        # ==============================================
        # ORIGINAL USER REQUEST
        # ==============================================

        html += format_html(
            """
            <div style="
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 12px;
                padding: 15px;
            ">

                <div style="
                    color: #1d4ed8;
                    font-weight: 700;
                    margin-bottom: 8px;
                ">
                    User
                </div>

                <div style="
                    color: #374151;
                    line-height: 1.6;
                    white-space: pre-wrap;
                ">
                    {}
                </div>

                <div style="
                    color: #6b7280;
                    font-size: 12px;
                    margin-top: 8px;
                ">
                    Original request
                </div>

            </div>
            """,
            obj.message,
        )

        # ==============================================
        # ALL REPLIES
        # ==============================================

        for reply in replies:

            reply_time = self.format_datetime(
                reply.created_at
            )

            # ------------------------------------------
            # ADMIN REPLY
            # ------------------------------------------

            if reply.is_admin:

                html += format_html(
                    """
                    <div style="
                        background: #ecfdf5;
                        border: 1px solid #86efac;
                        border-radius: 12px;
                        padding: 15px;
                    ">

                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            gap: 15px;
                            margin-bottom: 8px;
                        ">

                            <strong style="
                                color: #166534;
                            ">
                                Admin
                            </strong>

                            <span style="
                                color: #6b7280;
                                font-size: 12px;
                            ">
                                {}
                            </span>

                        </div>

                        <div style="
                            color: #374151;
                            line-height: 1.6;
                            white-space: pre-wrap;
                        ">
                            {}
                        </div>

                    </div>
                    """,
                    reply_time,
                    reply.message,
                )

            # ------------------------------------------
            # USER REPLY
            # ------------------------------------------

            else:

                html += format_html(
                    """
                    <div style="
                        background: #eff6ff;
                        border: 1px solid #93c5fd;
                        border-radius: 12px;
                        padding: 15px;
                    ">

                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            gap: 15px;
                            margin-bottom: 8px;
                        ">

                            <strong style="
                                color: #1d4ed8;
                            ">
                                User
                            </strong>

                            <span style="
                                color: #6b7280;
                                font-size: 12px;
                            ">
                                {}
                            </span>

                        </div>

                        <div style="
                            color: #374151;
                            line-height: 1.6;
                            white-space: pre-wrap;
                        ">
                            {}
                        </div>

                    </div>
                    """,
                    reply_time,
                    reply.message,
                )

        html += "</div>"

        return mark_safe(html)

    # ==================================================
    # ADMIN REPLY BOX
    # ==================================================

    @admin.display(
        description="Send reply to user"
    )
    def admin_reply_box(self, obj):

        request = getattr(
            self,
            "_current_request",
            None,
        )

        csrf_token = ""

        if request:
            csrf_token = get_token(request)

        reply_url = reverse(
            "admin:support_supportrequest_send_reply",
            args=[obj.pk],
        )

        textarea_id = (
            f"admin-reply-message-{obj.pk}"
        )

        function_name = (
            f"sendAdminReply{obj.pk}"
        )

        return format_html(
            """
            <div style="
                max-width: 900px;
                padding: 18px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            ">

                <textarea
                    id="{}"
                    rows="5"
                    placeholder="Type your reply to the user..."
                    style="
                        width: 100%;
                        box-sizing: border-box;
                        padding: 12px;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        resize: vertical;
                        font-size: 14px;
                    "
                ></textarea>

                <div style="
                    margin-top: 12px;
                ">

                    <button
                        type="button"
                        onclick="{}()"
                        style="
                            background: #166534;
                            color: white;
                            border: 0;
                            border-radius: 8px;
                            padding: 10px 18px;
                            font-weight: 600;
                            cursor: pointer;
                        "
                    >
                        Send Reply
                    </button>

                </div>

            </div>

            <script>
                function {}() {{

                    const textarea =
                        document.getElementById("{}");

                    const message =
                        textarea.value.trim();

                    if (!message) {{
                        alert(
                            "Reply message cannot be empty."
                        );
                        return;
                    }}

                    const form =
                        document.createElement("form");

                    form.method = "POST";
                    form.action = "{}";

                    const csrf =
                        document.createElement("input");

                    csrf.type = "hidden";
                    csrf.name = "csrfmiddlewaretoken";
                    csrf.value = "{}";

                    const messageInput =
                        document.createElement("input");

                    messageInput.type = "hidden";
                    messageInput.name = "admin_message";
                    messageInput.value = message;

                    form.appendChild(csrf);
                    form.appendChild(messageInput);

                    document.body.appendChild(form);

                    form.submit();
                }}
            </script>
            """,
            textarea_id,
            function_name,
            function_name,
            textarea_id,
            reply_url,
            csrf_token,
        )

    # ==================================================
    # KEEP CURRENT REQUEST
    # ==================================================

    def change_view(
        self,
        request,
        object_id,
        form_url="",
        extra_context=None,
    ):

        self._current_request = request

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context,
        )


# ======================================================
# SUPPORT REPLY ADMIN
# ======================================================

@admin.register(SupportReply)
class SupportReplyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "support_request",
        "sender",
        "message_short",
        "created_at",
    )

    list_filter = (
        "is_admin",
        "created_at",
    )

    search_fields = (
        "message",
        "user__username",
        "user__email",
        "support_request__subject",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "support_request",
        "user",
        "message",
        "is_admin",
        "created_at",
    )

    fieldsets = (
        (
            "Reply",
            {
                "fields": (
                    "support_request",
                    "user",
                    "message",
                    "is_admin",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    @admin.display(
        description="Sender"
    )
    def sender(self, obj):

        if obj.is_admin:
            return "Admin"

        return "User"

    @admin.display(
        description="Message"
    )
    def message_short(self, obj):

        if len(obj.message) > 80:
            return (
                obj.message[:80]
                + "..."
            )

        return obj.message