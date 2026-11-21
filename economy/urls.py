from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ItemViewSet, test_multiple_scraping_view, test_scraper_view

router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item")

urlpatterns = [
    path("test-scrape", test_scraper_view, name="test-scrape"),
    path(
        "test_multiple_scraping",
        test_multiple_scraping_view,
        name="test-multiple-scrape",
    ),
    path("", include(router.urls)),
]
