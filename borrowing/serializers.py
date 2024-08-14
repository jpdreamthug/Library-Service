from django.utils import timezone
from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


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
            "expected_return_date",
            "book",
            "user"
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer()

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
        user = self.context['request'].user
        book = attrs.get("book")

        if Borrowing.objects.filter(user=user, book=book, actual_return_date__isnull=True).exists():
            raise serializers.ValidationError("You have already borrowed this book.")

        if book.inventory <= 0:
            raise serializers.ValidationError("The book is out of stock")

        borrow_date = timezone.now().date()

        expected_return_date = attrs.get("expected_return_date")
        actual_return_date = None

        Borrowing.validate_dates(
            borrow_date,
            expected_return_date,
            actual_return_date,
            serializers.ValidationError
        )
        attrs["borrow_date"] = borrow_date

        return attrs

    def create(self, validated_data):
        book = validated_data.get("book")
        book.inventory -= 1
        book.save()
        return super().create(validated_data)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", )
