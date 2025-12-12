from django.test import TestCase
from django.contrib.auth import get_user_model
from django.apps import apps


class ReviewHistoryTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='tester', password='pass')
		self.Review = apps.get_model('reviews', 'Review')
		self.ReviewHistory = apps.get_model('reviews', 'ReviewHistory')

	def test_history_created_on_create_and_delete(self):
		# create a review
		r = self.Review.objects.create(user=self.user, rating=4, comment='Nice')
		# a history record should exist for create
		created = self.ReviewHistory.objects.filter(review_pk=r.pk, action='created').exists()
		self.assertTrue(created, 'ReviewHistory entry for created review missing')

		# delete the review (capture pk before deletion)
		pk = r.pk
		r.delete()
		deleted = self.ReviewHistory.objects.filter(review_pk=pk, action='deleted').exists()
		self.assertTrue(deleted, 'ReviewHistory entry for deleted review missing')

