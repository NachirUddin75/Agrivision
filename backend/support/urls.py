from django.urls import path

from .views import (
    SupportRequestListCreateView,
    SupportReplyCreateView,
)


urlpatterns = [

    path(
        "",
        SupportRequestListCreateView.as_view(),
        name="support-list-create",
    ),

    path(
        "<int:support_id>/reply/",
        SupportReplyCreateView.as_view(),
        name="support-reply-create",
    ),

]