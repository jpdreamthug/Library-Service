from django.urls import path

from payment.views import PaymentViewSet

payment_list = PaymentViewSet.as_view({"get": "list"})
payment_detail = PaymentViewSet.as_view({"get": "retrieve"})

urlpatterns = [
    path("", payment_list, name="payment-list"),
    path("<int:pk>/", payment_detail, name="payment-detail"),
]

app_name = "payments"
