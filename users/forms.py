from django import forms
from .models import Profile


class ProfilePictureForm(forms.ModelForm):
    """
    Form for uploading a profile picture.
    user: The user associated with the profile.
    image: The profile image file.
    """
    
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }
        labels = {
            'image': 'Profile Picture'
        }
