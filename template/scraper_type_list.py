from template.scraper_type import *
from template.scraper_category import *

class MetaData:
    category_list: list[ScraperCategory] = []
    scraper_type_list: list[ScraperType] = []

    @staticmethod
    def get_scraper_type_in_category(category: ScraperCategory) -> list[ScraperType]:
        ret = []

        for scraper_type in MetaData.scraper_type_list:
            if scraper_type.name in category.scraper_collection_names:
                ret.append(scraper_type)

        return ret

    @staticmethod
    def get_scraper_type_in_category_name(category_name: str) -> list[ScraperType]:
        category = None
        for cate in MetaData.category_list:
            if cate.name == category_name:
                category = cate
                break
        
        if category == None:
            return []

        ret = []

        for scraper_type in MetaData.scraper_type_list:
            if scraper_type.name in category.scraper_collection_names:
                ret.append(scraper_type)
        return ret
    
    @staticmethod
    def name_to_scraper_type(scraper_name: str) -> ScraperType:
        for type_ in MetaData.scraper_type_list:
            if type_.name == scraper_name:
                return type_
        return None