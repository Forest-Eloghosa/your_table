from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from .models import Review
from django.utils import timezone
from django.apps import apps
from django.contrib import messages


class ReviewListView(ListView):
	model = Review
	template_name = 'reviews/review_list.html'
	context_object_name = 'reviews'


class ReviewCreateView(CreateView):
	model = Review
	fields = ['rating', 'comment', 'image']
	template_name = 'reviews/review_form.html'
	success_url = reverse_lazy('reviews:review_list')

	def dispatch(self, request, *args, **kwargs):
		if request.method == 'POST' and not request.user.is_authenticated:
			return redirect_to_login(request.get_full_path())
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		# Ensure the user has at least one completed (past) booking before allowing a review
		Booking = apps.get_model('bookings', 'Booking')
		has_completed = False
		try:
			base_manager = getattr(Booking, 'all_objects', Booking.objects)
			has_completed = base_manager.filter(user=self.request.user, date__lt=timezone.now(), is_deleted=False).exists()
		except Exception:
			# If bookings app not available or check fails, default to False (deny)
			has_completed = False

		if not has_completed:
			messages.error(self.request, "You can only leave a review after completing a booking.")
			return redirect('reviews:review_list')

		form.instance.user = self.request.user
		return super().form_valid(form)
