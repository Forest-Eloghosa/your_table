from django.contrib.auth import get_user_model
from django.test import TestCase

from reviews.models import Review, ReviewHistory


class ReviewHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="pass")

    def test_history_created_on_create_and_delete(self):
        review = Review.objects.create(user=self.user, rating=4, comment="Nice")

        created = ReviewHistory.objects.filter(review_pk=review.pk, action="created").exists()
        self.assertTrue(created, "ReviewHistory entry for created review missing")

        pk = review.pk
        review.delete()
        deleted = ReviewHistory.objects.filter(review_pk=pk, action="deleted").exists()
        self.assertTrue(deleted, "ReviewHistory entry for deleted review missing")

    def test_str_uses_guest_name_for_anonymous(self):
        review = Review.objects.create(guest_name="Walk-in", rating=5, comment="Great meal")
        self.assertEqual(str(review), "Review(Walk-in, 5)")