from django.db.models import Q
from rest_framework import filters


class BorrowingFilterBackend(filters.BaseFilterBackend):
    """
    Custom filter backend for filtering Borrowing records.

    The filter applies the following rules:

    1. **Active Borrowings**:
        - If the `is_active` query parameter is "true" or "1", only
        borrowings with `actual_return_date` as `NULL` are included
        (i.e., active borrowings).
        - If `is_active` is "false" or "0", only borrowings with a non-null
        `actual_return_date` are included (i.e., completed borrowings).

    2. **User-Specific Filtering**:
        - If the `user_id` query parameter is provided and the user
        is an admin, filter the borrowings to include only those
        with the specified `user_id`.
        - If the user is not an admin, the `user_id` parameter is ignored.

    3. **Current User Filtering**:
        - Non-admin users will only see borrowings associated with
        their own user account.
    """

    def filter_queryset(self, request, queryset, view):
        is_admin = request.user.is_staff or request.user.is_superuser
        is_active = request.query_params.get("is_active", "").lower()
        user_id = request.query_params.get("user_id")

        if is_active in ["true", "1"]:
            queryset = queryset.filter(actual_return_date__isnull=True)
        elif is_active in ["false", "0"]:
            queryset = queryset.filter(~Q(actual_return_date__isnull=True))

        if user_id and is_admin:
            queryset = queryset.filter(user_id=user_id)

        if not is_admin:
            queryset = queryset.filter(user=request.user)

        return queryset
