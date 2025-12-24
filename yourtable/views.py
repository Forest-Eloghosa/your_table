from django.shortcuts import render


def handler404(request, exception=None):
    """Render a friendly 404 page using the global layout.

    Keeps existing site colors and components by extending base.html.
    """
    return render(request, '404.html', status=404)


def handler500(request):
    """Render a friendly 500 page using the global layout.

    Active when DEBUG=False. Keeps site styling and provides quick navigation.
    """
    return render(request, '500.html', status=500)


def handler403(request, exception=None):
    """Render a friendly 403 page for forbidden access."""
    return render(request, '403.html', status=403)
