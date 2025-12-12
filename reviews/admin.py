from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('user', 'rating', 'created_at')
	list_filter = ('rating', 'created_at')
	search_fields = ('user__username', 'comment')

from .models import ReviewHistory


@admin.register(ReviewHistory)
class ReviewHistoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'review_pk', 'user', 'action', 'timestamp')
	list_filter = ('action', 'timestamp')
	readonly_fields = ('review', 'review_pk', 'user', 'action', 'timestamp', 'data')
