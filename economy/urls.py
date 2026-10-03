from django.urls import path

from .views import test_scraper_view

urlpatterns = [
    path("test-scrape", test_scraper_view, name="test-scrape"),
]
