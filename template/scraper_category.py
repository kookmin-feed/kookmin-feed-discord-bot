
class ScraperCategory:

    def __init__(self, name: str, korean_name: str, scraper_collection_names: list):
        self.name = name
        self.korean_name = korean_name
        self.scraper_collection_names = scraper_collection_names

    def json_to_scraper_category(self, json):
        data = dict(json)

        self.name = data["name"]
        self.korean_name = data["korean_name"]
        self.scraper_collection_names = data["scraper_collection_names"]
