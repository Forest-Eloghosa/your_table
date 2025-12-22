from django.db import models
from django.conf import settings


class Review(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	guest_name = models.CharField(max_length=100, blank=True, help_text="Name for anonymous reviews")
	rating = models.PositiveSmallIntegerField(default=5)
	comment = models.TextField(blank=True)
	image = models.ImageField(upload_to='reviews/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		name = self.user.get_full_name() if self.user else self.guest_name or "Anonymous"
		return f"Review({name}, {self.rating})"


class ReviewHistory(models.Model):
	ACTIONS = [
		('created', 'Created'),
		('updated', 'Updated'),
		('deleted', 'Deleted'),
	]

	review = models.ForeignKey(Review, null=True, blank=True, on_delete=models.SET_NULL, related_name='history')
	review_pk = models.IntegerField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	action = models.CharField(max_length=10, choices=ACTIONS)
	timestamp = models.DateTimeField(auto_now_add=True)
	data = models.JSONField(null=True, blank=True)

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		return f"{self.get_action_display()} review {self.review_pk} at {self.timestamp.isoformat()}"
