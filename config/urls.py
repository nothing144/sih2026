from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve as media_serve


urlpatterns = [

    path("admin/", admin.site.urls),

    path(
        "api/auth/",
        include("users.urls")
    ),
     path(
        "api/batteries/",
        include("batteries.urls"),
    ),
    path("api/analysis/", include("analysis.urls")),
   path("api/passport/", include("passport.urls")),
]

# Serve uploaded BMS CSV files from the same host.
# NOTE: fine for a single-instance deployment. For multi-instance or
# serverless deployments, move MEDIA_ROOT to object storage
# (e.g. Supabase Storage/S3) instead.
if not settings.DEBUG:
    urlpatterns += [
        path(
            "media/<path:path>",
            media_serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
