from django import forms
from .models import Profile


class ProfilePictureForm(forms.ModelForm):
    """Form for uploading a profile picture."""
    
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }
        labels = {
            'image': 'Profile Picture'
        }
