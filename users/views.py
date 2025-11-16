from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. You can now log in.')
            return redirect('account_login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
 