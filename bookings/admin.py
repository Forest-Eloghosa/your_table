from django.contrib import admin
from .models import (
    Booking,
    BookingImage,
    Cancellation,
    BookingHistory,
)

# Register your models here.

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurant", "date", "guests")
    list_filter = ("restaurant",)
    search_fields = ("user__username", "restaurant__name")


@admin.register(BookingImage)
class BookingImageAdmin(admin.ModelAdmin):
    list_display = ("id", "booking")


@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ("booking", "canceled_at")


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "booking_pk", "user", "action", "timestamp")
    list_filter = ("action", "timestamp")
    readonly_fields = ("booking", "booking_pk", "user", "action", "timestamp", "data")

