from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    View for creating a new user. No authentication required.
    """
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Create a new user",
        description="Create a new user account. "
                    "No authentication is required.",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: "Bad request"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


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
        summary="Retrieve and update user information",
        description="Retrieve and update the information"
                    " of the currently authenticated user."
                    " Requires authentication.",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update user information",
        description="Update the information of the currently "
                    "authenticated user. Requires authentication.",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: "Bad request",
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update user information",
        description="Partially update the information of "
                    "the currently authenticated user using PATCH. "
                    "Requires authentication.",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: "Bad request",
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
