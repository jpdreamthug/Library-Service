from datetime import timezone
from unittest import TestCase

from jsonschema.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
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
            expected_return_date="2024-09-01",
        )
        self.borrowing_url = reverse(
            "borrowings:borrowing-detail", args=[self.borrowing.id]
        )
        self.borrowing_list_url = reverse("borrowings:borrowing-list")
        self.token = str(RefreshToken.for_user(self.normal_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_list_borrowings(self):
        response = self.client.get(self.borrowing_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["book"], str(self.book))

    def test_retrieve_borrowing(self):
        response = self.client.get(self.borrowing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["book"]["title"], self.book.title)
        self.assertEqual(response.data["user"], self.normal_user.id)

    def test_create_borrowing(self):
        data = {
            "book": self.book.id,
            "expected_return_date": "2024-09-10",
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
        }
        response = self.client.post(self.borrowing_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "The book is out of stock", response.data["non_field_errors"]
        )

    def test_permission_denied_create_borrowing(self):
        self.client.credentials()
        data = {
            "book": self.book.id,
            "expected_return_date": "2024-09-10",
        }
        response = self.client.post(self.borrowing_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_borrowings(self):
        admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        response = self.client.get(self.borrowing_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", inventory=1, daily_fee=5.0
        )

    def test_borrowing_with_invalid_dates(self):
        borrow_date = timezone.now().date()
        expected_return_date = borrow_date - timezone.timedelta(days=1)

        with self.assertRaises(ValidationError) as context:
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                borrow_date=borrow_date,
                expected_return_date=expected_return_date,
            )
        self.assertIn(
            "Expected return date must be after borrow date.",
            context.exception.messages,
        )

    def test_borrowing_with_actual_return_before_borrow(self):
        borrow_date = timezone.now().date()
        actual_return_date = borrow_date - timezone.timedelta(days=1)

        borrowing = Borrowing(
            user=self.user,
            book=self.book,
            borrow_date=borrow_date,
            expected_return_date=borrow_date + timezone.timedelta(days=7),
            actual_return_date=actual_return_date,
        )

        with self.assertRaises(ValidationError) as context:
            borrowing.clean()

        self.assertIn(
            "Actual return date cannot be before borrow date.",
            context.exception.messages,
        )


class BorrowingAlreadyBorrowedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", inventory=1, daily_fee=5.0
        )

    def test_borrowing_already_borrowed_book(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date()
            + timezone.timedelta(days=7),
        )

        with self.assertRaises(ValidationError) as context:
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                expected_return_date=timezone.now().date()
                + timezone.timedelta(days=7),
            )
        self.assertIn(
            "This book is already borrowed.",
            context.exception.messages,
        )


class BorrowingFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="password"
        )
        self.user = User.objects.create_user(
            email="user@example.com", password="password"
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", inventory=1, daily_fee=5.0
        )

    def test_filter_active_borrowings(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date()
            + timezone.timedelta(days=7),
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            reverse("borrowing-list"), {"is_active": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_user_id_admin(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date()
            + timezone.timedelta(days=7),
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            reverse("borrowing-list"), {"user_id": self.user.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_current_user(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date()
            + timezone.timedelta(days=7),
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("borrowing-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
