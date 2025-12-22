from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import Http404

from .models import Booking, BookingHistory
from .forms import BookingForm
from .email_utils import send_booking_cancellation_email

# Create your views here.
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        # Include soft-deleted bookings in the list so users can see "Already deleted"
        # Use the `all_objects` manager when available, otherwise fall back to default.
        base_manager = getattr(Booking, 'all_objects', Booking.objects)
        return base_manager.filter(user=self.request.user).order_by("date")


class BookingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"

    def get_queryset(self):
        """Include soft-deleted bookings so users can view history of cancelled bookings."""
        base_manager = getattr(Booking, 'all_objects', Booking.objects)
        return base_manager.all()

    def test_func(self):
        booking = self.get_object()
        return booking.user == self.request.user

    def get(self, request, *args, **kwargs):
        """If the booking doesn't exist, redirect to booking list with a friendly message."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.error(request, "No booking found matching the query. You can create a new booking.")
            return redirect('bookings:booking_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Show history entries for this booking made by the current user
        history_items = []
        try:
            qs = BookingHistory.objects.filter(
                booking_pk=self.object.pk,
                user=self.request.user
            ).order_by('-timestamp')[:25]
            import json
            from django.utils.html import escape

            for h in qs:
                # prepare a pretty JSON string for the template (template will escape it)
                pretty = ''
                if h.data:
                    try:
                        pretty = json.dumps(h.data, indent=2, ensure_ascii=False, default=str)
                    except Exception:
                        try:
                            pretty = str(h.data)
                        except Exception:
                            pretty = ''
                username = None
                try:
                    username = h.user.username if h.user else None
                except Exception:
                    username = None
                history_items.append({
                    'action_display': h.get_action_display(),
                    'timestamp': h.timestamp,
                    'data_pretty': pretty,
                    'username': username,
                })
        except Exception:
            history_items = []
        ctx['user_history'] = history_items
        return ctx


class BookingCreateView(CreateView):
    """Allow anonymous users to view the create page (so promotional carousel shows),
    but require login for POST (submitting a booking). Anonymous POSTs are redirected
    to the login page and after login the user can complete the booking.
    """
    model = Booking
    template_name = "bookings/create_booking.html"
    form_class = BookingForm
    success_url = reverse_lazy("bookings:booking_success")

    def dispatch(self, request, *args, **kwargs):
        # Allow GET for everyone (so carousel and info are visible),
        # but protect POST so only authenticated users can submit the form.
        if request.method == 'POST' and not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # At this point user is authenticated (POST was allowed), attach user
        form.instance.user = self.request.user
        resp = super().form_valid(form)
        messages.success(self.request, "Booking created successfully.")
        return resp
    

class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    template_name = "bookings/create_booking.html"
    form_class = BookingForm

    def test_func(self):
        booking = self.get_object()
        return booking.user == self.request.user

    def get_success_url(self):
        return reverse_lazy("bookings:booking_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Your booking was updated.")
        return resp


class BookingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Booking
    template_name = "bookings/booking_delete.html"
    success_url = reverse_lazy("bookings:booking_list")

    def test_func(self):
        booking = self.get_object()
        return booking.user == self.request.user
    
    def get_queryset(self):
        # Use the full queryset (including soft-deleted records) so the view
        # can locate the booking object even if it's been soft-deleted earlier.
        try:
            return Booking.all_objects.all()
        except Exception:
            # Fallback to default manager if all_objects is not available
            return Booking.objects.all()

    def delete(self, request, *args, **kwargs):
        # Get booking before deletion to send email
        booking = self.get_object()
        # Perform delete (soft-delete implemented on model) and show confirmation
        resp = super().delete(request, *args, **kwargs)
        # Send cancellation email
        if send_booking_cancellation_email(booking):
            messages.success(request, "Booking cancelled successfully. A confirmation email has been sent.")
        else:
            messages.success(request, "Booking cancelled successfully.")
        return resp


from django.views.generic import TemplateView

class BookingSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "bookings/success.html"



