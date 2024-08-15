from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from borrowing.models import Borrowing
from book.models import Book
from user.models import User


class BorrowingAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com", password="userpassword"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=1.50,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.normal_user,
            book=self.book,
            expected_return_date="2024-09-01"
        )
        self.borrowing_url = reverse("borrowings:borrowing-detail", args=[self.borrowing.id])
        self.borrowing_list_url = reverse("borrowings:borrowing-list")
        self.token = str(RefreshToken.for_user(self.normal_user).access_token)
        self.client.credentials(HTTP_AUTHORIZE=f"Bearer {self.token}")

    def test_list_borrowings(self):
        response = self.client.get(self.borrowing_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['book'], str(self.book))

    def test_retrieve_borrowing(self):
        response = self.client.get(self.borrowing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['title'], self.book.title)
        self.assertEqual(response.data['user'], self.normal_user.id)

    def test_create_borrowing(self):
        data = {
            "book": self.book.id,
            "expected_return_date": "2024-09-10",
            "user": self.normal_user.id,
        }
        response = self.client.post(self.borrowing_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_create_borrowing_out_of_stock(self):
        self.book.inventory = 0
        self.book.save()

        data = {
            "book": self.book.id,
            "expected_return_date": "2024-09-10",
            "user": self.normal_user.id,
        }
        response = self.client.post(self.borrowing_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The book is out of stock", response.data['non_field_errors'])

    def test_permission_denied_create_borrowing(self):
        self.client.credentials()
        data = {
            "book": self.book.id,
            "expected_return_date": "2024-09-10",
        }
        response = self.client.post(self.borrowing_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_borrowings(self):
        self.client.credentials(HTTP_AUTHORIZE=f"Bearer {str(RefreshToken.for_user(self.admin_user).access_token)}")
        response = self.client.get(self.borrowing_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
