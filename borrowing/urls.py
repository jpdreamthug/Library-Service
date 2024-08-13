from django.urls import path, include
from rest_framework import routers

from borrowing.views import BorrowingViewSet

borrowing_list_create = BorrowingViewSet.as_view({'get': 'list', "post": "create"})
borrowing_detail = BorrowingViewSet.as_view({'get': 'retrieve'})
# borrowing_create = BorrowingViewSet.as_view({'post': 'create'})

urlpatterns = [
    path("", borrowing_list_create, name="borrowing-list"),
    path("<int:pk>/", borrowing_detail, name="borrowing-detail"),
]

app_name = "borrowings"
