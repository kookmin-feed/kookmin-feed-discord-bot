from typing import Optional, Dict, Type
from template.scrapper_type import ScrapperType
from web_scrapper.web_scrapper import WebScrapper
from web_scrapper.academic_notice_scrapper import AcademicNoticeScrapper
from web_scrapper.sw_notice_scrapper import SWNoticeScrapper
from web_scrapper.rss_notice_scrapper import RSSNoticeScrapper
from web_scrapper.archi_all_notice_scrapper import ArchiNoticeScrapper
from web_scrapper.cms_academic_notice_scrapper import CMSAcademicNoticeScrapper
from web_scrapper.me_academic_notice_scrapper import MEAcademicNoticeScrapper
from web_scrapper.cs_scholarship_notice_scrapper import CsScholarshipNoticeScrapper
from web_scrapper.linc_notice_scrapper import LincNoticeScrapper
from web_scrapper.id_academic_notice_scrapper import IdAcademicNoticeScrapper
from web_scrapper.vcd_academic_notice_scrapper import VcdAcademicNoticeScrapper
from web_scrapper.mcraft_academic_notice_scrapper import McraftAcademicNoticeScrapper


class ScrapperFactory:
    """스크래퍼 객체를 생성하는 팩토리 클래스"""

    _instance = None
    _scrapper_classes: Dict[str, Type[WebScrapper]] = {
        "AcademicNoticeScrapper": AcademicNoticeScrapper,
        "CsScholarshipNoticeScrapper": CsScholarshipNoticeScrapper,
        "SWNoticeScrapper": SWNoticeScrapper,
        "RSSNoticeScrapper": RSSNoticeScrapper,
        "ArchiNoticeScrapper": ArchiNoticeScrapper,
        "CMSAcademicNoticeScrapper": CMSAcademicNoticeScrapper,
        "MEAcademicNoticeScrapper": MEAcademicNoticeScrapper,
        "LincNoticeScrapper": LincNoticeScrapper,
        "IdAcademicNoticeScrapper": IdAcademicNoticeScrapper,
        "VcdAcademicNoticeScrapper": VcdAcademicNoticeScrapper,
        "McraftAcademicNoticeScrapper": McraftAcademicNoticeScrapper,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_scrapper(self, scrapper_type: ScrapperType) -> Optional[WebScrapper]:
        """스크래퍼 타입에 맞는 스크래퍼 객체를 생성합니다."""
        url = scrapper_type.get_url()

        # RSS 스크래퍼인 경우
        if scrapper_type.name.endswith("_RSS"):
            return RSSNoticeScrapper(url, scrapper_type)

        # 일반 스크래퍼인 경우
        else:
            scrapper_class = self._scrapper_classes.get(
                scrapper_type.get_scrapper_class_name()
            )

            if not scrapper_class:
                return None

            return scrapper_class(url)
