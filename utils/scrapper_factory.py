from typing import Optional, Dict, Type
import os
import importlib
from utils.scrapper_type import ScrapperType
from utils.web_scrapper import WebScrapper
from utils.rss_notice_scrapper import RSSNoticeScrapper
import sys
from pathlib import Path


class ScrapperFactory:
    """스크래퍼 객체를 생성하는 팩토리 클래스"""

    _instance = None
    _scrapper_classes: Dict[str, Type[WebScrapper]] = {}

    @classmethod
    def _initialize_scrapper_classes(cls):
        """web_scrapper 폴더의 모든 스크래퍼 클래스를 동적으로 import하여 초기화합니다."""
        # RSS 스크래퍼 추가 (utils 폴더에 있음)
        cls._scrapper_classes["RSSNoticeScrapper"] = RSSNoticeScrapper

        # web_scrapper 폴더 경로 설정
        current_dir = Path(__file__).parent.parent
        scrapper_dir = current_dir / "web_scrapper"

        # Python path에 web_scrapper 폴더 추가
        sys.path.append(str(current_dir))

        try:
            # web_scrapper 폴더의 모든 .py 파일을 검사
            for filename in os.listdir(scrapper_dir):
                if filename.endswith("_scrapper.py") and not filename.startswith("__"):
                    # 파일 이름에서 .py 확장자 제거
                    module_name = filename[:-3]

                    try:
                        # 모듈 import
                        module = importlib.import_module(f"web_scrapper.{module_name}")

                        # snake_case를 CamelCase로 변환
                        class_name = "".join(
                            word.capitalize() for word in module_name.split("_")
                        )

                        # 해당 클래스가 모듈에 존재하는지 확인하고 추가
                        if hasattr(module, class_name):
                            cls._scrapper_classes[class_name] = getattr(
                                module, class_name
                            )
                        else:
                            print(
                                f"Class {class_name} not found in module {module_name}"
                            )

                    except Exception as e:
                        print(f"Error importing module {module_name}: {e}")

        except Exception as e:
            print(f"Error scanning web_scrapper directory: {e}")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_scrapper_classes()
        return cls._instance

    def create_scrapper(self, scrapper_type: ScrapperType) -> Optional[WebScrapper]:
        """스크래퍼 타입에 맞는 스크래퍼 객체를 생성합니다."""
        url = scrapper_type.get_url()

        scrapper_class = self._scrapper_classes.get(
            scrapper_type.get_scrapper_class_name()
        )

        if not scrapper_class:
            return None

        # RSS 스크래퍼인 경우 scrapper_type도 전달
        if scrapper_type.name.endswith("_RSS"):
            return scrapper_class(url, scrapper_type)

        # 일반 스크래퍼인 경우
        return scrapper_class(url)
