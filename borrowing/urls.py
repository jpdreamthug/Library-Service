from django.urls import path

from borrowing.views import BorrowingViewSet

borrowing_list_create = BorrowingViewSet.as_view({'get': 'list', "post": "create"})
borrowing_detail = BorrowingViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    path("", borrowing_list_create, name="borrowing-list"),
    path("<int:pk>/", borrowing_detail, name="borrowing-detail"),
]

app_name = "borrowings"
