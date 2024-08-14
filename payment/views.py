from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

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
        is_admin = (self.request.user.is_staff
                    or self.request.user.is_superuser)
        if not is_admin:
            queryset = queryset.filter(borrowing__user=self.request.user)

        return queryset
