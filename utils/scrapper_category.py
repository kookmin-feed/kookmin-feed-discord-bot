from enum import Enum
from typing import List, Dict
from utils.scrapper_type import ScrapperType


class ScrapperCategory(Enum):
    """스크래퍼 카테고리를 정의하는 열거형 클래스"""

    UNIVERSITY_CATEGORY = (
        "국민대",
        [
            ScrapperType.UNIVERSITY_ACADEMIC,
            ScrapperType.UNIVERSITY_SCHOLARSHIP,
        ],
    )

    COMPUTERSCIENCE_CATEGORY = (
        "소프트웨어융합대학",
        [
            ScrapperType.COMPUTERSCIENCE_ACADEMIC_RSS,
            ScrapperType.SOFTWARECENTERED_ACADEMIC,
        ],
    )

    BUSINESSADMINISTRATION_CATEGORY = (
        "경영대학",
        [
            ScrapperType.BUSINESSADMINISTRATION_ACADEMIC_RSS,
        ],
    )

    ARCHITECTURE_CATEGORY = (
        "건축대학",
        [
            ScrapperType.ARCHITECTURE_ACADEMIC,
        ],
    )

    SOCIALSCIENCE_CATEGORY = (
        "사회과학대학",
        [
            ScrapperType.SOCIALSCIENCE_PUBLICADMINISTRATION_ACADEMIC,
        ],
    )

    CREATIVEENGINEERING_CATEGORY = (
        "창의공과대학",
        [
            ScrapperType.CREATIVEENGINEERING_MECHANICAL_ACADEMIC,
            ScrapperType.CREATIVEENGINEERING_ELECTRICAL_ACADEMIC_RSS,
            ScrapperType.CREATIVEENGINEERING_ADVANCEDMATERIALS_ACADEMIC,
        ],
    )

    DESIGN_CATEGORY = (
        "조형대학",
        [
            ScrapperType.DESIGN_INDUSTRIAL_ACADEMIC,
            ScrapperType.DESIGN_VISUAL_ACADEMIC,
            ScrapperType.DESIGN_METALWORK_ACADEMIC,
        ],
    )

    OTHERS_CATEGORY = (
        "사업단 및 부속기관",
        [
            ScrapperType.LINC_ACADEMIC,
        ],
    )

    AUTOMOTIVEENGINEERING_CATEGORY = (
        "자동차융합대학",
        [
            ScrapperType.AUTOMATIVEENGINEERING_ACADEMIC,
        ],
    )

    def __init__(self, korean_name: str, scrapper_types: List[ScrapperType]):
        self.korean_name = korean_name
        self.scrapper_types = scrapper_types

    @classmethod
    def get_category_choices(cls) -> List[Dict]:
        """디스코드 명령어용 카테고리 선택지 목록을 반환합니다."""
        return [
            {"name": category.korean_name, "value": category.name} for category in cls
        ]

    @classmethod
    def get_scrapper_choices(cls, category_name: str) -> List[Dict]:
        """특정 카테고리의 스크래퍼 선택지 목록을 반환합니다."""
        try:
            category = cls[category_name]
            return [
                {"name": scrapper_type.get_korean_name(), "value": scrapper_type.name}
                for scrapper_type in category.scrapper_types
            ]
        except KeyError:
            return []

    @classmethod
    def get_all_scrappers(cls) -> List[ScrapperType]:
        """모든 스크래퍼 타입을 반환합니다."""
        all_scrappers = []
        for category in cls:
            all_scrappers.extend(category.scrapper_types)
        return all_scrappers

    @classmethod
    def find_category_by_scrapper(
        cls, scrapper_type: ScrapperType
    ) -> "ScrapperCategory":
        """스크래퍼 타입이 속한 카테고리를 반환합니다."""
        for category in cls:
            if scrapper_type in category.scrapper_types:
                return category
        return None
