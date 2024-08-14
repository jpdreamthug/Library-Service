from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
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
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
