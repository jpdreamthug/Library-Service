"""
URL configuration for library_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter


def api_root(request):
    return JsonResponse(
        {
            "admin": request.build_absolute_uri(reverse("admin:index")),
            "api/": request.build_absolute_uri("api/"),
            "api/books/": request.build_absolute_uri("api/books/"),
            "api/borrowings/": request.build_absolute_uri("api/borrowings/"),
            "api/payments/": request.build_absolute_uri("api/payments/"),
            "api/users/": request.build_absolute_uri(reverse("users:api_root")),
            "api/doc/swagger/": request.build_absolute_uri("api/doc/swagger/"),
            "api/doc/redoc/": request.build_absolute_uri("api/doc/redoc/"),
        }
    )


router = DefaultRouter()

urlpatterns = [
    path("", api_root, name="api_root"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/books/", include("book.urls", namespace="books")),
    path("api/borrowings/", include("borrowing.urls", namespace="borrowings")),
    path("api/users/", include("user.urls", namespace="users")),
    path("api/payments/", include("payment.urls", namespace="payments")),
    path(
        "api/doc/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/doc/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
] + debug_toolbar_urls()
