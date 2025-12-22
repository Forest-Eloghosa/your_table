from django import forms
from django.forms import widgets
from django.forms.widgets import SplitDateTimeWidget
from .models import Booking, BookingImage
from django.utils import timezone
from django.core.exceptions import ValidationError


class BookingForm(forms.ModelForm):
    # Use a single datetime-local input for simpler, well-labeled control
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control', 'id': 'id_date'}
        )
    )

    class Meta:
        model = Booking
        fields = ['restaurant', 'date', 'guests', 'special_requests']
        widgets = {
            'restaurant': forms.Select(attrs={'class': 'form-select'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_date(self):
        dt = self.cleaned_data.get('date')
        if dt and dt < timezone.now():
            raise ValidationError('Booking date/time cannot be in the past.')
        return dt


class BookingImageForm(forms.ModelForm):
    class Meta:
        model = BookingImage
        fields = ['image']
