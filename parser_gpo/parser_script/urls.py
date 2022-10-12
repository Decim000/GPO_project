from django.urls import path
from .views import crawler, generate_url

urlpatterns = [
    path('crawler/', crawler),
    path('test-url/', generate_url),
]