from django.http import JsonResponse
from django.urls import path, reverse
from rest_framework_simplejwt import views as jwt_views

from user.views import CreateUserView, CreateTokenView, ManageUserView

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", CreateTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path(
        "jwt_token/",
        jwt_views.TokenObtainPairView.as_view(),
        name="jwt_token_obtain_pair",
    ),
    path(
        "jwt_token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="jwt_token_refresh",
    ),
    path(
        "jwt_token/verify/",
        jwt_views.TokenVerifyView.as_view(),
        name="jwt_token_verify",
    ),
]