from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.utils import timezone
from django.apps import apps
from .models import Review


class ReviewListView(ListView):
	"""
	List all reviews.
	Authenticated users see all reviews.
	Anonymous users see only reviews with a guest_name.
	"""
	model = Review
	template_name = 'reviews/review_list.html'
	context_object_name = 'reviews'


class ReviewCreateView(CreateView):
	"""
	Allow both authenticated and anonymous users to create reviews.
	Authenticated users have their user field set automatically.
	Anonymous users must provide a guest_name.
	"""
	model = Review
	template_name = 'reviews/review_form.html'
	success_url = reverse_lazy('reviews:review_list')

	def get_form_fields(self):
		"""Return form fields based on authentication status."""
		if self.request.user.is_authenticated:
			return ['rating', 'comment', 'image']
		else:
			return ['guest_name', 'rating', 'comment', 'image']

	def get_form_class(self):
		"""Dynamically return form class with appropriate fields."""
		from django import forms
		fields = self.get_form_fields()
		return type('ReviewForm', (forms.ModelForm,), {
			'Meta': type('Meta', (), {
				'model': Review,
				'fields': fields,
				'widgets': {
					'guest_name': forms.TextInput(attrs={'placeholder': 'Your name', 'required': True}),
					'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)], attrs={'class': 'form-select'}),
					'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
					'image': forms.FileInput(attrs={'class': 'form-control'}),
				}
			})
		})

	def form_valid(self, form):
		if self.request.user.is_authenticated:
			form.instance.user = self.request.user
		# For anonymous users, guest_name is set by form
		return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	"""
	Allow authenticated users to edit their own reviews.
	"""
	model = Review
	template_name = 'reviews/review_form.html'
	success_url = reverse_lazy('reviews:review_list')
	fields = ['rating', 'comment', 'image']

	def test_func(self):
		"""Only the review owner can edit their review."""
		review = self.get_object()
		return review.user == self.request.user

	def form_valid(self, form):
		messages.success(self.request, 'Review updated successfully!')
		return super().form_valid(form)


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	"""
	Allow authenticated users to delete their own reviews.
	"""
	model = Review
	template_name = 'reviews/review_confirm_delete.html'
	success_url = reverse_lazy('reviews:review_list')

	def test_func(self):
		"""Only the review owner can delete their review."""
		review = self.get_object()
		return review.user == self.request.user

	def delete(self, request, *args, **kwargs):
		messages.success(request, 'Review deleted successfully!')
		return super().delete(request, *args, **kwargs)

