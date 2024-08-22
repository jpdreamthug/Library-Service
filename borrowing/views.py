import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stripe import StripeError

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
from payment.models import Payment
from payment.services import create_payment_session


stripe.api_key = settings.STRIPE_SECRET_KEY


@extend_schema(
    tags=["Borrowings"]
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
        "create_payment": BorrowingReturnSerializer,
    }

    @extend_schema(
        summary="List all borrowings",
        description="Retrieve a list of all borrowings with details"
        " such as book and user. Non-admin users will"
        " only see their own borrowings.",
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by active borrowings (true/1)"
                " or completed borrowings (false/0)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID if user is admin",
                required=False,
                type=int,
            ),
        ],
        responses={
            200: BorrowingListSerializer(many=True),
            400: "Bad request",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new borrowing",
        description="Create a new borrowing record."
                    "Requires authentication.",
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        borrowing_id = response.data.get("id")
        borrowing = Borrowing.objects.get(id=borrowing_id)

        try:
            payment = create_payment_session(
                borrowing,
                request,
                Payment.Type.PAYMENT
            )
        except StripeError as e:
            borrowing.delete()
            return Response(
                {"detail": "Error while creating payment session"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {"payment_url": payment.session_url},
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Retrieve a borrowing",
        description="Retrieve details of a specific "
                    "borrowing record using its ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Return a borrowed book",
        description="Mark a borrowed book as returned. "
        "This updates the `actual_return_date` "
        "and book inventory.",
    )
    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path="return",
    )
    @transaction.atomic
    def return_borrowing_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"message": "Book has already been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.book.inventory += 1
        time_now = timezone.now().date()
        borrowing.actual_return_date = time_now
        borrowing.save()
        borrowing.book.save()

        if borrowing.is_overdue:
            payment = create_payment_session(
                borrowing,
                request,
                Payment.Type.FINE
            )
            return Response(
                {
                    "session_url": payment.session_url,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Book returned successfully",
                "actual_return_date": time_now,
            },
            status=status.HTTP_200_OK,
        )
