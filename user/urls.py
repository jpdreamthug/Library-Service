from django.urls import path

from user.views import (
    CreateUserView,
    ManageUserView,
    CustomTokenRefreshView,
    CustomTokenObtainPairView,
    CustomTokenVerifyView,
)

app_name = "users"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user_create"),
    path("me/", ManageUserView.as_view(), name="user_manage"),
    path(
        "token/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "token/verify/",
        CustomTokenVerifyView.as_view(),
        name="token_verify",
    ),
]
