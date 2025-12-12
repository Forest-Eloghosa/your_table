from django.contrib import admin
from .models import (
    Booking,
    BookingImage,
    Table,
    Reservation,
    Payment,
    BookingStatus,
    Feedback,
    CancellationPolicy,
    Cancellation,
    SpecialOffer,
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


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "number", "capacity")
    list_filter = ("restaurant",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("booking", "table")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "transaction_id")


@admin.register(BookingStatus)
class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ("booking", "status", "updated_at")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("booking", "rating", "created_at")


@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ("restaurant",)


@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ("booking", "canceled_at")


@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "discount_percentage", "valid_from", "valid_until")


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "booking_pk", "user", "action", "timestamp")
    list_filter = ("action", "timestamp")
    readonly_fields = ("booking", "booking_pk", "user", "action", "timestamp", "data")

