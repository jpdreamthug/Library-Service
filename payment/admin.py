from django.contrib import admin

from payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "type",
        "borrowing",
        "session_url",
        "session_id",
        "money_to_pay",
    )
    list_filter = ("status", "type", "borrowing")
    search_fields = ("borrowing__book__title", "borrowing__user__email")
