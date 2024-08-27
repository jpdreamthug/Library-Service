from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user",
            "book",
        )


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "actual_return_date",
            "expected_return_date",
            "book",
            "user",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["book"] = str(instance.book)
        return rep


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    payments = PaymentSerializer(many=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user",
            "book",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    def validate(self, attrs):
        user = self.context["request"].user
        book = attrs.get("book")

        if Payment.objects.filter(
            borrowing__user=user, status=Payment.Status.PENDING
        ).exists():
            raise serializers.ValidationError(
                "You have pending payments. "
                "Please complete them before borrowing a new book."
            )

        if Borrowing.objects.filter(
            user=user, book=book, actual_return_date__isnull=True
        ).exists():
            raise serializers.ValidationError(
                "You have already borrowed this book."
            )

        if book.inventory <= 0:
            raise serializers.ValidationError("The book is out of stock")

        borrow_date = timezone.now().date()
        attrs["borrow_date"] = borrow_date

        Borrowing.validate_dates(
            borrow_date,
            attrs.get("expected_return_date"),
            actual_return_date=None,
            error=serializers.ValidationError,
        )

        return attrs

    def create(self, validated_data):
        book = validated_data.get("book")
        book.inventory -= 1
        book.save(update_fields=["inventory"])

        return super().create(validated_data)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",)
