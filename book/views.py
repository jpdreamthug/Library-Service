from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


@extend_schema(
    tags=["Books"],
    summary="Books API",
    description="Endpoints related to managing books within the library system.",
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    @method_decorator(cache_page(60 * 5, key_prefix="books_list_view"))
    @extend_schema(
        summary="List all books",
        description="Retrieve a list of all books.",
        responses={200: BookSerializer(many=True), 400: "Bad request"},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new book",
        description="Create a new book entry. Requires admin privileges.",
    )
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Retrieve a book",
        description="Retrieve the details of a specific book using its ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update a book",
        description="Update the details of a specific book using its ID. Requires admin privileges.",
    )
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partially update a book",
        description="Partially update the details of a specific book using its ID. Requires admin privileges.",
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a book",
        description="Delete a specific book using its ID. Requires admin privileges.",
    )
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
