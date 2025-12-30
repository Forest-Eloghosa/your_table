from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, BookingHistory
from menu.models import Restaurant


class BookingViewTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="testuser", password="pass1234")
        self.other_user = self.User.objects.create_user(username="otheruser", password="pass5678")
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant",
            description="",
            address="",
            phone="",
            website="",
        )

    def _make_booking(self, user=None, date=None):
        """Helper to create a booking."""
        user = user or self.user
        when = date or timezone.now() + timedelta(hours=3)
        return Booking.objects.create(
            user=user,
            restaurant=self.restaurant,
            date=when,
            guests=2,
            special_requests="",
        )

    def test_booking_list_requires_login(self):
        """Anonymous users are redirected to login when accessing booking list."""
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_booking_list_shows_user_bookings_only(self):
        """Users see only their own bookings in the list."""
        self.client.login(username="testuser", password="pass1234")
        my_booking = self._make_booking(user=self.user)
        other_booking = self._make_booking(user=self.other_user)

        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, my_booking.restaurant.name)
        self.assertNotContains(response, f"Booking for {other_booking.guests}")

    def test_booking_detail_requires_ownership(self):
        """Users cannot view other users' bookings."""
        booking = self._make_booking(user=self.other_user)
        self.client.login(username="testuser", password="pass1234")

        response = self.client.get(reverse("bookings:booking_detail", args=[booking.pk]))
        self.assertEqual(response.status_code, 403)

    def test_booking_create_get_accessible_anonymous(self):
        """Anonymous users can view the create booking page (GET)."""
        response = self.client.get(reverse("bookings:booking_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create booking")

    def test_booking_create_post_requires_login(self):
        """Anonymous users redirected to login when submitting booking form."""
        future = timezone.now() + timedelta(hours=5)
        response = self.client.post(
            reverse("bookings:booking_create"),
            {
                "restaurant": self.restaurant.id,
                "date": future.strftime("%Y-%m-%dT%H:%M"),
                "guests": 3,
                "special_requests": "Window seat",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_booking_create_authenticated_user_success(self):
        """Authenticated users can create bookings."""
        self.client.login(username="testuser", password="pass1234")
        future = timezone.now() + timedelta(hours=5)
        response = self.client.post(
            reverse("bookings:booking_create"),
            {
                "restaurant": self.restaurant.id,
                "date": future.strftime("%Y-%m-%dT%H:%M"),
                "guests": 4,
                "special_requests": "Allergy note",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(user=self.user, guests=4).exists())

    def test_booking_update_requires_ownership(self):
        """Users can only update their own bookings."""
        booking = self._make_booking(user=self.other_user)
        self.client.login(username="testuser", password="pass1234")

        future = timezone.now() + timedelta(hours=10)
        response = self.client.post(
            reverse("bookings:booking_update", args=[booking.pk]),
            {
                "restaurant": self.restaurant.id,
                "date": future.strftime("%Y-%m-%dT%H:%M"),
                "guests": 5,
                "special_requests": "Updated",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_booking_delete_soft_deletes_booking(self):
        """Deleting a booking marks it as soft-deleted."""
        booking = self._make_booking(user=self.user)
        self.client.login(username="testuser", password="pass1234")

        response = self.client.post(reverse("bookings:booking_delete", args=[booking.pk]))
        self.assertEqual(response.status_code, 302)

        booking.refresh_from_db()
        self.assertTrue(booking.is_deleted)
        self.assertIsNotNone(booking.deleted_at)

    def test_booking_delete_creates_history_entry(self):
        """Deleting a booking creates a history entry."""
        booking = self._make_booking(user=self.user)
        self.client.login(username="testuser", password="pass1234")

        self.client.post(reverse("bookings:booking_delete", args=[booking.pk]))

        history = BookingHistory.objects.filter(booking_pk=booking.pk, action="deleted")
        self.assertTrue(history.exists())
