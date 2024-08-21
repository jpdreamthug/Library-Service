from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    @method_decorator(vary_on_headers("Authorize"))
    @method_decorator(cache_page(60 * 5, key_prefix="books"))
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
        request=BookSerializer,
        responses={201: BookSerializer, 400: "Bad request"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a book",
        description="Retrieve the details of a specific book using its ID.",
        responses={200: BookSerializer, 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update a book",
        description="Update the details of a specific book "
        "using its ID. Requires admin privileges.",
        request=BookSerializer,
        responses={200: BookSerializer, 400: "Bad request", 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a book",
        description="Delete a specific book using its ID. "
        "Requires admin privileges.",
        responses={204: "No Content", 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update a book",
        description="Partially update the details of a specific "
        "book using its ID. Requires admin privileges.",
        request=BookSerializer,
        responses={200: BookSerializer, 400: "Bad request", 404: "Not Found"},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
