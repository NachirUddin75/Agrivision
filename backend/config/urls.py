from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

# Load Agrivision admin configuration.
# This executes config/admin.py and applies FRONTEND_URL.
from . import admin as agrivision_admin_config


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/accounts/",
        include("accounts.urls"),
    ),

    path(
        "api/soil/",
        include("soil.urls"),
    ),

    path("api/crops/", include("crops.urls")),

    path(
    "api/support/",
    include("support.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )