from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

# Load Agrivision admin configuration.
# This executes config/admin.py and applies FRONTEND_URL.
from . import admin as agrivision_admin_config


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/soil/", include("soil.urls")),
    path("api/crops/", include("crops.urls")),
    path("api/support/", include("support.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]