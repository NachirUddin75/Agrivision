import os

from django.contrib import admin


admin.site.site_header = "Agrivision Administration"
admin.site.site_title = "Agrivision Admin"
admin.site.index_title = "Welcome to Agrivision Administration"

# Get the frontend URL from .env
admin.site.site_url = os.getenv(
    "FRONTEND_URL",
    "/",
)