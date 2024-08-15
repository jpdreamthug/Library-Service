from django.http import JsonResponse
from django.urls import path
from rest_framework.reverse import reverse
from rest_framework_simplejwt import views as jwt_views

from user.views import CreateUserView, ManageUserView


def api_root(request):
    return JsonResponse(
        {
            "register": request.build_absolute_uri(reverse("users:create")),
            "me": request.build_absolute_uri(reverse("users:manage")),
            "token_obtain": request.build_absolute_uri(
                reverse("users:token_obtain_pair")
            ),
            "token_refresh": request.build_absolute_uri(
                reverse("users:token_refresh")
            ),
            "token_verify": request.build_absolute_uri(
                reverse("users:token_verify")
            ),
        }
    )


app_name = "users"

urlpatterns = [
    path("", api_root, name="api_root"),
    path("register/", CreateUserView.as_view(), name="create"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path(
        "token/",
        jwt_views.TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "token/verify/",
        jwt_views.TokenVerifyView.as_view(),
        name="token_verify",
    ),
]
