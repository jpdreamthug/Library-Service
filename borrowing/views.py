import stripe
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
from payment.services import create_stripe_session

stripe.api_key = settings.STRIPE_SECRET_KEY


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

    @method_decorator(vary_on_headers("Authorize"))
    @method_decorator(cache_page(60 * 5, key_prefix="borrowings"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        borrowing_id = response.data.get("id")
        borrowing = Borrowing.objects.get(id=borrowing_id)

        payment = create_stripe_session(borrowing, request)

        return HttpResponseRedirect(redirect_to=payment.session_url)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path="return",
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

    # @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    # def create_payment(self, request, pk=None):
    #     domain = "http://localhost:8000"
    #     borrowing = self.get_object()
    #     money_to_pay = borrowing.calculate_payment()
    #     payment = Payment.objects.create(
    #         borrowing=borrowing,
    #         money_to_pay=money_to_pay,
    #         status=Payment.Status.PENDING,
    #         type=Payment.Type.PAYMENT,
    #     )
    #     checkout_session = stripe.checkout.Session.create(
    #         line_items=[
    #             {
    #                 "price_data": {
    #                     "currency": "usd",
    #                     "unit_amount": money_to_pay,
    #                     "product_data": {
    #                         "name": f"Book: {borrowing.book.title}",
    #                     },
    #                 },
    #                 "quantity": 1,
    #             },
    #         ],
    #         mode="payment",
    #         success_url=domain + "?success=true",
    #         cancel_url=domain + "?canceled=true",
    #     )
    #     payment.session_id = checkout_session.id
    #     payment.session_url = checkout_session.url
    #     payment.save()
    #
    #     return JsonResponse({"id": checkout_session.id})
