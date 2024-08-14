from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied

from borrowing.filters import BorrowingFilterBackend
from borrowing.mixins import GenericMethodsMixin
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
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
    permission_classes = [IsAuthenticated]
    filter_backends = [BorrowingFilterBackend]
    action_serializers = {
        "list": BorrowingListSerializer,
        "retrieve": BorrowingDetailSerializer,
        "create": BorrowingCreateSerializer,
        "return_borrowing_book": BorrowingReturnSerializer,
    }

    @method_decorator(cache_page(60 * 5, key_prefix="borrowings"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"], detail=True, permission_classes=[IsAuthenticated]
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
                    "actual_return_date": time_now,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Book has already been returned"},
            status=status.HTTP_400_BAD_REQUEST,
        )
