from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingDetailSerializer
from borrowing.mixins import GenericMethodsMixin


class BorrowingViewSet(
    GenericMethodsMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    action_serializers = {
        "list": BorrowingListSerializer,
        "retrieve": BorrowingDetailSerializer
    }
    permission_classes = (IsAuthenticated,)

