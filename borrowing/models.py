from random import randint

from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, Q
from rest_framework.exceptions import ValidationError

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(expected_return_date__gt=models.F("borrow_date")),
                name="expected_return_after_borrow",
            ),
            CheckConstraint(
                check=Q(actual_return_date__gte=models.F("borrow_date"))
                | Q(actual_return_date__isnull=True),
                name="actual_return_after_borrow_or_null",
            ),
        ]

    @staticmethod
    def validate_dates(borrow_date, expected_return_date, actual_return_date, error):
        if not borrow_date:
            raise error({"borrow_date": "Borrow date must be specified."})

        if not expected_return_date:
            raise error(
                {"expected_return_date": "Expected return date must be specified."}
            )

        if actual_return_date and actual_return_date < borrow_date:
            raise error(
                {
                    "actual_return_date": "Actual return date cannot be before borrow date."
                }
            )

        if borrow_date > expected_return_date:
            raise error(
                {
                    "expected_return_date": "Expected return date must be after borrow date."
                }
            )

    def clean(self):
        super().clean()
        self.validate_dates(
            self.borrow_date,
            self.expected_return_date,
            self.actual_return_date,
            ValidationError,
        )

    def __str__(self):
        return (
            f"Borrowed '{self.book}' on {self.borrow_date}, "
            f"expected return by {self.expected_return_date}"
        )

    def calculate_payment(self) -> float:
        return round(randint(500, 50000), 2)

    def calculate_fine(self) -> float:
        return self.calculate_payment()
