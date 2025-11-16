from django.urls import path
from .views import (
    BookingListView,
    BookingDetailView,
    BookingCreateView,
    BookingUpdateView,
    BookingDeleteView,
    BookingSuccessView,
)

app_name = 'bookings'

urlpatterns = [
    path("", BookingListView.as_view(), name="booking_list"),
    path("<int:pk>/", BookingDetailView.as_view(), name="booking_detail"),
    path("new/", BookingCreateView.as_view(), name="booking_create"),
    path("create/", BookingCreateView.as_view(), name="booking_create"),
    path("<int:pk>/edit/", BookingUpdateView.as_view(), name="booking_update"),
    path("<int:pk>/delete/", BookingDeleteView.as_view(), name="booking_delete"),
    path("success/", BookingSuccessView.as_view(), name="booking_success"),
]
