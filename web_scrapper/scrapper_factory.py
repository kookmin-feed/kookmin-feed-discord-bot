from typing import Optional, Dict, Type
from template.scrapper_type import ScrapperType
from web_scrapper.web_scrapper import WebScrapper
from web_scrapper.academic_notice_scrapper import AcademicNoticeScrapper
from web_scrapper.sw_notice_scrapper import SWNoticeScrapper
from web_scrapper.rss_notice_scrapper import RSSNoticeScrapper
from web_scrapper.archi_all_notice_scrapper import ArchiNoticeScrapper
from web_scrapper.cms_academic_notice_scrapper import CMSAcademicNoticeScrapper
from web_scrapper.me_academic_notice_scrapper import MEAcademicNoticeScrapper
class ScrapperFactory:
    """스크래퍼 객체를 생성하는 팩토리 클래스"""
    
    _instance = None
    _scrapper_classes: Dict[str, Type[WebScrapper]] = {
        'AcademicNoticeScrapper': AcademicNoticeScrapper,
        'SWNoticeScrapper': SWNoticeScrapper,
        'RSSNoticeScrapper': RSSNoticeScrapper,
        'ArchiNoticeScrapper': ArchiNoticeScrapper,
        'CMSAcademicNoticeScrapper': CMSAcademicNoticeScrapper,
        'MEAcademicNoticeScrapper': MEAcademicNoticeScrapper,
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def create_scrapper(self, scrapper_type: ScrapperType) -> Optional[WebScrapper]:
        """스크래퍼 타입에 맞는 스크래퍼 객체를 생성합니다."""
        url = scrapper_type.get_url()
        scrapper_class = self._scrapper_classes.get(scrapper_type.get_scrapper_class_name())
        
        if not scrapper_class:
            return None
            
        # RSS 스크래퍼인 경우 scrapper_type도 전달
        if scrapper_type.name.endswith('_RSS'):
            return scrapper_class(url, scrapper_type)
            
        # 일반 스크래퍼인 경우
        return scrapper_class(url) 