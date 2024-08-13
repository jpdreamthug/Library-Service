from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.settings import api_settings

from user.serializers import AuthTokenSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    View for creating a new user. No authentication required.
    """
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [AllowAny]


class CreateTokenView(ObtainAuthToken):
    """
    View for obtaining authentication token for a user. No authentication required.
    """
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer
    authentication_classes = []
    permission_classes = [AllowAny]


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating the currently authenticated user's information.
    Requires authentication using token.
    """
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
