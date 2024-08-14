from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied

from borrowing.mixins import GenericMethodsMixin
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    GenericMethodsMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    action_serializers = {
        "list": BorrowingListSerializer,
        "retrieve": BorrowingDetailSerializer,
        "create": BorrowingCreateSerializer,
    }

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        serializer.save(user=self.request.user)
