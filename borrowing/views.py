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

    def get_queryset(self):
        queryset = self.queryset
        is_admin = self.request.user.is_staff or self.request.user.is_superuser
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)

        if user_id and is_admin:
            queryset = queryset.filter(user_id=user_id)

        if not is_admin:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        serializer.save(user=self.request.user)
