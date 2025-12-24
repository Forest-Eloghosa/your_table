"""
URL configuration for yourtable project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', include('about.urls', namespace='about')),
    path('bookings/', include('bookings.urls')),
    path('menu/', include('menu.urls')),
    path('users/', include('users.urls')),
    path("accounts/", include("allauth.urls")),
    path('reviews/', include('reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        # STATICFILES_DIRS may be a list of Path objects; convert to str for static().
        static_root = settings.STATICFILES_DIRS[0]
        urlpatterns += static(settings.STATIC_URL, document_root=str(static_root))
    except Exception:
        # Fallback: do nothing if STATICFILES_DIRS is not present or empty.
        pass

    # Custom error handlers (active when DEBUG=False)
    handler404 = 'yourtable.views.handler404'
    handler500 = 'yourtable.views.handler500'
    handler403 = 'yourtable.views.handler403'
