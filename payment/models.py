from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        PAID = "PAID", _("Paid")

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", _("Payment")
        FINE = "FINE", _("Fine")

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PAYMENT,
    )
    borrowing_id = models.IntegerField()
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment {self.id} - {self.type} - {self.status}"
