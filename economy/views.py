from django.http import JsonResponse

from .scraper import Region, Scraper


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
        scraper = Scraper(region=region)
        data = scraper.scrape_item(int(item_id))
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
