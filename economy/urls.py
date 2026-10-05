from django.urls import path

from .views import test_multiple_scraping_view, test_scraper_view

urlpatterns = [
    path("test-scrape", test_scraper_view, name="test-scrape"),
    path(
        "test_multiple_scraping",
        test_multiple_scraping_view,
        name="test-multiple-scrape",
    ),
]
