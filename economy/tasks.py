from django.core.management import call_command


def run_scraper():
    """Wraper to run scrape command."""
    call_command("scrape_economy")
