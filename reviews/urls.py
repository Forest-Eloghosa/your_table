from django.urls import path
from .views import ReviewListView, ReviewCreateView, ReviewUpdateView, ReviewDeleteView

app_name = 'reviews'

urlpatterns = [
    path('', ReviewListView.as_view(), name='review_list'),
    path('create/', ReviewCreateView.as_view(), name='review_create'),
    path('<int:pk>/edit/', ReviewUpdateView.as_view(), name='review_update'),
    path('<int:pk>/delete/', ReviewDeleteView.as_view(), name='review_delete'),
]
