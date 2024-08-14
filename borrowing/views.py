from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.mixins import GenericMethodsMixin
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer, BorrowingReturnSerializer,
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
    permission_classes = (IsAuthenticated,)
    action_serializers = {
        "list": BorrowingListSerializer,
        "retrieve": BorrowingDetailSerializer,
        "create": BorrowingCreateSerializer,
        "return_borrowing_book": BorrowingReturnSerializer
    }

    def get_queryset(self):
        """
        All non-admins can see only their borrowings. Admins can see all
        borrowings and use filter by user_id.
        is_active parameter for filtering by active borrowings
        """
        queryset = self.queryset
        is_admin = self.request.user.is_staff or self.request.user.is_superuser
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)

        if user_id and is_admin:
            queryset = queryset.filter(user_id=user_id)

        if not is_admin:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    @transaction.atomic
    def return_borrowing_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date is None:
            borrowing.book.inventory += 1
            time_now = timezone.now().date()
            borrowing.actual_return_date = time_now
            borrowing.save()
            borrowing.book.save()
            return Response(
                {
                    "message": "Book returned successfully",
                    "actual_return_date": time_now
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Book has already been returned"},
            status=status.HTTP_400_BAD_REQUEST
        )
