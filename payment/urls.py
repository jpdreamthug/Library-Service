from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payments")

urlpatterns = router.urls

app_name = "payments"
