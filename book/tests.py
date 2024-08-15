from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from book.models import Book

User = get_user_model()

class BookServiceTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password"
        )
        self.admin_user = User.objects.create_superuser(
            email="adminuser@example.com",
            password="adminpassword"
        )
        self.client.force_authenticate(user=self.admin_user)
        self.book = Book.objects.create(
            title="Original Title",
            author="Original Author",
            cover="HARD",
            inventory=10,
            daily_fee=1.99
        )
        self.book_list_url = reverse("book:book-list")
        self.book_detail_url = lambda pk: reverse("book:book-detail", kwargs={"pk": pk})

    def test_list_books(self):
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "title": "New Book",
            "author": "Author Name",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 1.99,
        }
        response = self.client.post("/api/books/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_book_as_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.book_list_url, {"title": "New Book", "inventory": 10})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_as_admin(self):
        data = {
            "title": "Updated Title",
            "author": "Updated Author",
            "cover": "SOFT",
            "inventory": 15,
            "daily_fee": 2.50,
        }
        response = self.client.put(f"/api/books/{self.book.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_book_as_non_admin(self):
        book = Book.objects.create(title="Existing Book", inventory=5)
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.book_detail_url(book.id), {"title": "Updated Book", "inventory": 8})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_as_admin(self):
        book = Book.objects.create(title="Existing Book", inventory=5)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.book_detail_url(book.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_book_as_non_admin(self):
        book = Book.objects.create(title="Existing Book", inventory=5)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.book_detail_url(book.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
