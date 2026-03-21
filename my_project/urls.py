from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),

    # Main site
    path("", include("blog_app.urls")),

    # Store pages
    path("store/", include("store.urls")),

    # Stripe webhook at /webhook/
    path("", include("store.webhook_urls")),
]