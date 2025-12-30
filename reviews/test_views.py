from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from reviews.models import Review, ReviewHistory


class ReviewViewTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="reviewer", password="pass1234")
        self.other_user = self.User.objects.create_user(username="otherreviewer", password="pass5678")

    def test_review_list_accessible_to_all(self):
        """Review list is accessible to both authenticated and anonymous users."""
        response = self.client.get(reverse("reviews:review_list"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_can_create_review_with_guest_name(self):
        """Anonymous users can submit reviews with a guest name."""
        response = self.client.post(
            reverse("reviews:review_create"),
            {
                "guest_name": "Anonymous Visitor",
                "rating": 5,
                "comment": "Great experience!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(guest_name="Anonymous Visitor").exists())

    def test_authenticated_user_review_has_user_set(self):
        """Authenticated users' reviews are associated with their user account."""
        self.client.login(username="reviewer", password="pass1234")
        response = self.client.post(
            reverse("reviews:review_create"),
            {
                "rating": 4,
                "comment": "Very good service",
            },
        )
        self.assertEqual(response.status_code, 302)
        review = Review.objects.filter(user=self.user).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 4)

    def test_authenticated_user_can_update_own_review(self):
        """Users can update their own reviews."""
        review = Review.objects.create(user=self.user, rating=3, comment="Initial review")
        self.client.login(username="reviewer", password="pass1234")

        response = self.client.post(
            reverse("reviews:review_update", args=[review.pk]),
            {
                "rating": 5,
                "comment": "Updated review - much better!",
            },
        )
        self.assertEqual(response.status_code, 302)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Updated review - much better!")

    def test_user_cannot_update_others_review(self):
        """Users cannot update reviews they don't own."""
        review = Review.objects.create(user=self.other_user, rating=4, comment="Other's review")
        self.client.login(username="reviewer", password="pass1234")

        response = self.client.post(
            reverse("reviews:review_update", args=[review.pk]),
            {
                "rating": 1,
                "comment": "Trying to hijack",
            },
        )
        self.assertEqual(response.status_code, 403)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)

    def test_authenticated_user_can_delete_own_review(self):
        """Users can delete their own reviews."""
        review = Review.objects.create(user=self.user, rating=3, comment="To be deleted")
        self.client.login(username="reviewer", password="pass1234")

        response = self.client.post(reverse("reviews:review_delete", args=[review.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_user_cannot_delete_others_review(self):
        """Users cannot delete reviews they don't own."""
        review = Review.objects.create(user=self.other_user, rating=5, comment="Other's review")
        self.client.login(username="reviewer", password="pass1234")

        response = self.client.post(reverse("reviews:review_delete", args=[review.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

    def test_review_update_requires_login(self):
        """Anonymous users cannot update reviews."""
        review = Review.objects.create(user=self.user, rating=4, comment="User's review")

        response = self.client.get(reverse("reviews:review_update", args=[review.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_review_delete_requires_login(self):
        """Anonymous users cannot delete reviews."""
        review = Review.objects.create(user=self.user, rating=4, comment="User's review")

        response = self.client.get(reverse("reviews:review_delete", args=[review.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_review_history_created_on_update(self):
        """Updating a review creates a history entry."""
        review = Review.objects.create(user=self.user, rating=3, comment="Original")
        self.client.login(username="reviewer", password="pass1234")

        # Clear any existing history from creation
        initial_count = ReviewHistory.objects.filter(review_pk=review.pk).count()

        self.client.post(
            reverse("reviews:review_update", args=[review.pk]),
            {
                "rating": 5,
                "comment": "Updated",
            },
        )

        # Check that new history entry was created
        updated_count = ReviewHistory.objects.filter(review_pk=review.pk).count()
        self.assertGreater(updated_count, initial_count)
