from django.contrib import admin
from django.urls import path, include


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