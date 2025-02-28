from enum import Enum
from typing import Optional
from discord import app_commands


class ScrapperType(Enum):
    """스크래퍼 종류를 정의하는 열거형 클래스"""

    UNIVERSITY_ACADEMIC = (
        "university_academic",
        "대학 학사공지",
        "https://cs.kookmin.ac.kr/news/kookmin/academic/",
        "UniversityAcademicScrapper",
    )
    UNIVERSITY_SCHOLARSHIP = (
        "university_scholarship",
        "대학 장학공지",
        "https://cs.kookmin.ac.kr/news/kookmin/scholarship/",
        "UniversityScholarshipScrapper",
    )
    COMPUTERSCIENCE_ACADEMIC_RSS = (
        "computerscience_academic_rss",
        "소융대 학사공지",
        "https://cs.kookmin.ac.kr/news/notice/rss",
        "RSSNoticeScrapper",
    )
    SOFTWARECENTERED_ACADEMIC = (
        "softwarecentered_academic",
        "SW중심대학사업단 학사공지",
        "https://software.kookmin.ac.kr/software/bulletin/notice.do",
        "SoftwarecenteredAcademicScrapper",
    )
    BUSINESSADMINISTRATION_ACADEMIC_RSS = (
        "businessadministration_academic_rss",
        "경영대 학사공지",
        "https://biz.kookmin.ac.kr/community/notice/rss",
        "RSSNoticeScrapper",
    )
    ARCHITECTURE_ACADEMIC = (
        "architecture_academic",
        "건축대 학사공지",
        "https://archi.kookmin.ac.kr/life/notice/",
        "ArchitectureAcademicScrapper",
    )
    SOCIALSCIENCE_PUBLICADMINISTRATION_ACADEMIC = (
        "socialscience_publicadministration_academic",
        "행정학과 학사공지",
        "http://cms.kookmin.ac.kr/paap/notice/notice.do",
        "SocialsciencePublicadministrationAcademicScrapper",
    )
    CREATIVEENGINEERING_MECHANICAL_ACADEMIC = (
        "creativeengineering_mechanical_academic",
        "기계공학부 학사공지",
        "http://cms.kookmin.ac.kr/mech/bbs/notice.do",
        "CreativeengineeringMechanicalAcademicScrapper",
    )
    DESIGN_INDUSTRIAL_ACADEMIC = (
        "design_industrial_academic",
        "공업디자인학과 학사공지",
        "https://id.kookmin.ac.kr/id/intro/notice.do",
        "DesignIndustrialAcademicScrapper",
    )
    DESIGN_METALWORK_ACADEMIC = (
        "design_metalwork_academic",
        "금속공예학과 학사공지",
        "http://mcraft.kookmin.ac.kr/?page_id=516",
        "DesignMetalworkAcademicScrapper",
    )
    LINC_ACADEMIC = (
        "linc_academic",
        "LINC 3.0 사업단 학사공지",
        "https://linc.kookmin.ac.kr/main/menu?gc=605XOAS",
        "LincAcademicScrapper",
    )
    DESIGN_VISUAL_ACADEMIC = (
        "design_visual_academic",
        "시각디자인학과 학사공지",
        "https://vcd.kookmin.ac.kr/vcd/etc-board/vcdnotice.do",
        "DesignVisualAcademicScrapper",
    )
    CREATIVEENGINEERING_ELECTRICAL_ACADEMIC_RSS = (
        "creativeengineering_electrical_academic_rss",
        "전자공학부 학사공지",
        "https://ee.kookmin.ac.kr/community/board/notice/rss",
        "RSSNoticeScrapper",
    )
    AUTOMATIVEENGINEERING_ACADEMIC = (
        "automativeengineering_academic",
        "자동차융합대학 학사공지",
        "https://auto.kookmin.ac.kr/board/notice/?&pn=0",
        "AutomativeengineeringAcademicScrapper",
    )
    # 서브도메인 + (학과) 게시판 종류 + {rss, bs4(x)}

    def get_collection_name(self) -> str:
        """MongoDB 컬렉션 이름을 반환합니다."""
        return self.value[0]  # value는 tuple의 첫 번째 요소를 사용

    def get_korean_name(self) -> str:
        """스크래퍼 타입의 한글 이름을 반환합니다."""
        return self.value[1]

    def get_url(self) -> str:
        """스크래퍼의 URL을 반환합니다."""
        return self.value[2]

    def get_scrapper_class_name(self) -> str:
        """스크래퍼 클래스 이름을 반환합니다."""
        return self.value[3]

    @classmethod
    def from_str(cls, value: str) -> Optional["ScrapperType"]:
        """문자열로부터 ScrapperType을 생성합니다."""
        try:
            return cls[value.upper()]  # Enum의 value로 직접 생성
        except ValueError:
            return None

    @classmethod
    def get_choices(cls) -> list:
        """디스코드 명령어용 선택지 목록을 반환합니다."""
        return [
            app_commands.Choice(name=type.get_korean_name(), value=type.name)
            for type in cls
        ]

    @classmethod
    def get_active_scrappers(cls) -> list:
        """활성화된 스크래퍼 타입들을 반환합니다."""
        return list(cls)  # 모든 스크래퍼가 활성화됨
