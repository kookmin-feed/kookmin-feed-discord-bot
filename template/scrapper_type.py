from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from discord import app_commands

class ScrapperType(Enum):
    """스크래퍼 종류를 정의하는 열거형 클래스"""
    CS_ACADEMIC_NOTICE = ('cs_academic_notice','대학 학사공지', 'https://cs.kookmin.ac.kr/news/kookmin/academic/')
    CS_SW_NOTICE_RSS = ('cs_sw_notice_rss','소융대 학사공지', 'https://cs.kookmin.ac.kr/news/notice/rss')
    SOFTWARE_NOTICE = ('software_notice','SW중심대학사업단 공지', 'https://software.kookmin.ac.kr/software/bulletin/notice.do')
    BIZ_ALL_NOTICE_RSS = ('biz_all_notice_rss','경영대 학사공지', 'https://biz.kookmin.ac.kr/news/notice/rss')
    ARCHI_ALL_NOTICE = ('archi_all_notice','건축대 전체공지', 'https://archi.kookmin.ac.kr/life/notice/')
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

    @classmethod
    def from_str(cls, value: str) -> Optional['ScrapperType']:
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