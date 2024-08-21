import stripe
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.mixins import GenericMethodsMixin
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentViewSet(
    GenericMethodsMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    action_serializers = {"retrieve": PaymentDetailSerializer}

    def get_queryset(self):
        queryset = self.queryset
        is_admin = self.request.user.is_staff or self.request.user.is_superuser
        if not is_admin:
            queryset = queryset.filter(borrowing__user=self.request.user)

        return queryset

    @action(
        detail=False,
        methods=["GET"],
        url_path="success",
        url_name="payment-success",
    )
    def success(self, request):
        session_id = request.GET.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = stripe.checkout.Session.retrieve(session_id)
        payment = Payment.objects.filter(session_id=session_id).first()

        if not payment:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if session.payment_status == "paid":
            payment.status = Payment.Status.PAID
            payment.save()

            return Response(
                {"message": "Payment was successful"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Payment wasn't successful"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="cancel",
        url_name="payment-cancel",
    )
    def cancel(self, request):
        return Response(
            {"message": "Payment was canceled. You can pay within 24 hours."},
            status=status.HTTP_200_OK,
        )
