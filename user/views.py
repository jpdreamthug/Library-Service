from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.serializers import UserSerializer


@extend_schema(tags=["Users"])
class CreateUserView(generics.CreateAPIView):
    """
    This view allows users to create a new user account. No authentication is
    required to access this view. It uses the `UserSerializer` to handle the
    creation of the user.

    Methods:
        post: Create a new user with the provided data. The request should
        include the user's email and password. If successful, a new user is
        created and a 201 Created response is returned. If there are
        validation errors, an appropriate error response is returned.

    """

    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Create a new user",
        description="Create a new user account. "
        "No authentication is required.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["Users"])
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating the currently
    authenticated user's information.
    Requires authentication using token.
    """

    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Show information about user",
        description="Show information about user "
        "Authentication is required.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update user information",
        description="Update the information of the currently "
        "authenticated user. Requires authentication.",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update user information",
        description="Partially update the information of "
        "the currently authenticated user using PATCH. "
        "Requires authentication.",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    tags=["Authentication"],
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View for obtaining a JWT token pair.

    This view handles the generation of a new JWT token pair (access and
    refresh tokens) when provided with valid user credentials. It extends
    the default `TokenObtainPairView` provided by `rest_framework_simplejwt`
    to allow for any customizations if needed in the future.

    Methods:
        post: Accepts user credentials (username and password) and returns
        a JWT token pair. If the credentials are valid, it returns a 200 OK
        response with the access and refresh tokens. If the credentials
        are invalid, it returns a 401 Unauthorized response.
    """
    pass


@extend_schema(tags=["Authentication"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    View for refreshing a JWT access token.

    This view handles the refreshing of an existing JWT access token using
    a valid refresh token. It extends the default `TokenRefreshView` from
    `rest_framework_simplejwt` to accommodate any future customizations if
    needed.

    Methods:
        post: Accepts a refresh token and returns a new JWT access token.
        If the refresh token is valid, it returns a 200 OK response with
        the new access token. If the token is invalid or expired, it
        returns a 401 Unauthorized response.
        """
    pass


@extend_schema(tags=["Authentication"])
class CustomTokenVerifyView(TokenVerifyView):
    """
    View for verifying the validity of a JWT token.

    This view handles the verification of the validity of a JWT token.
    It checks whether the provided access or refresh token is valid.
    It extends the default `TokenVerifyView`from `rest_framework_simplejwt`
    to allow for potential future customizations.

    Methods:
        post: Accepts a JWT token and verifies its validity.
        Returns a 200 OK response if the token is valid. If the token is
        invalid or expired, it returns a 401 Unauthorized response.
    """
    pass
