from discord import app_commands

class ScraperType:

    scraper_type_list = []

    def __init__(self, korean_name: str = None,
                    scraper_colloction_name: str = None, scraper_type_name: str = None):
        self.korean_name = korean_name
        self.collection_name = scraper_colloction_name
        self.name = scraper_type_name

    def json_to_scraper_type(self, json):
        di = dict(json)

        self.korean_name = di['korean_name']
        self.collection_name = di['scraper_collection_name']
        self.collection_name = di['type_name']
