from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from bookings.forms import BookingForm
from bookings.models import Booking, BookingHistory
from menu.models import MenuCategory, Restaurant


class BookingFormTests(TestCase):
    def setUp(self):
        self.category = MenuCategory.objects.create(name="Mains", slug="mains")
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant",
            description="",
            address="",
            phone="",
            website="",
        )

    def test_booking_form_accepts_future_datetime(self):
        future = timezone.now() + timedelta(hours=2)
        form = BookingForm(
            data={
                "restaurant": self.restaurant.id,
                "date": future.strftime("%Y-%m-%dT%H:%M"),
                "guests": 4,
                "special_requests": "Window seat",
            }
        )

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["restaurant"], self.restaurant)
        self.assertEqual(form.cleaned_data["guests"], 4)

    def test_booking_form_rejects_past_datetime(self):
        past = timezone.now() - timedelta(hours=1)
        form = BookingForm(
            data={
                "restaurant": self.restaurant.id,
                "date": past.strftime("%Y-%m-%dT%H:%M"),
                "guests": 2,
                "special_requests": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)
        self.assertIn("past", form.errors["date"][0])


class BookingModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="alice", password="pass1234")
        self.category = MenuCategory.objects.create(name="Desserts", slug="desserts")
        self.restaurant = Restaurant.objects.create(
            name="Sweet Tooth",
            slug="sweet-tooth",
            description="",
            address="",
            phone="",
            website="",
        )

    def _make_booking(self, date=None):
        when = date or timezone.now() + timedelta(hours=3)
        return Booking.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            date=when,
            guests=3,
            special_requests="",
        )

    def test_clean_blocks_past_date(self):
        past = timezone.now() - timedelta(days=1)
        booking = Booking(
            user=self.user,
            restaurant=self.restaurant,
            date=past,
            guests=2,
            special_requests="",
        )

        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_history_created_on_save(self):
        booking = self._make_booking()
        history = BookingHistory.objects.filter(booking_pk=booking.pk, action="created")
        self.assertTrue(history.exists())

    def test_soft_delete_marks_flag_and_records_history(self):
        booking = self._make_booking()

        booking.delete()

        self.assertTrue(booking.is_deleted)
        self.assertIsNotNone(booking.deleted_at)
        history = BookingHistory.objects.filter(booking_pk=booking.pk, action="deleted")
        self.assertTrue(history.exists())