import random
import time

from django.http import JsonResponse

from .scraper import Region, Scraper, managed_browser


# Create your views here.
def test_scraper_view(request):
    region_param = request.GET.get("region", "eu").lower()
    item_id = request.GET.get("id", "859")

    try:
        region = Region[region_param.upper()]
    except ValueError:
        return JsonResponse(
            {"status": "error", "message": "Invalid region"}, status=400
        )

    try:
        with managed_browser(headless=False) as page:
            scraper = Scraper(page, region=region)
            data = scraper.scrape_item(int(item_id))
            return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def test_multiple_scraping_view(request):
    region_param = request.GET.get("region", "eu").lower()

    try:
        region = Region[region_param.upper()]
    except ValueError:
        return JsonResponse(
            {"status": "error", "message": "Invalid region"}, status=400
        )

    item_ids = ["812", "8120", "184802", "161958", "154858", "4681", "7924"]
    items_data = []

    with managed_browser(headless=False) as page:
        scraper = Scraper(page, region=region)
        try:
            for item_id in item_ids:
                print(f"ID: {item_id}")
                data = scraper.scrape_item(int(item_id))
                print(data)
                items_data.append(data)

                delay = random.uniform(1.5, 3.0)
                print(f"Waiting {delay:.2f} seconds before next item...\n")
                time.sleep(delay)
            return JsonResponse(items_data, safe=False)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
