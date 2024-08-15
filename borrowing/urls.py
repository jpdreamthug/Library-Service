from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing.views import BorrowingViewSet

router = DefaultRouter()
router.register(r"", BorrowingViewSet, basename="borrowings")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowings"
