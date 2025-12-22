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
					'rating': forms.Select(),
					'comment': forms.Textarea(attrs={'rows': 4}),
				}
			})
		})

	def form_valid(self, form):
		if self.request.user.is_authenticated:
			form.instance.user = self.request.user
		# For anonymous users, guest_name is set by form
		return super().form_valid(form)
