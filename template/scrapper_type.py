from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from discord import app_commands

class ScrapperType(Enum):
    """스크래퍼 종류를 정의하는 열거형 클래스"""
    ACADEMIC = 'academic'      # 학사공지
    SWACADEMIC = 'swAcademic' # SW학사공지
    SW = 'sw'                 # SW중심대학

    def get_korean_name(self) -> str:
        """스크래퍼 타입의 한글 이름을 반환합니다."""
        _KOREAN_NAMES = {
            'academic': '학사공지',
            'swAcademic': 'SW학사공지',
            'sw': 'SW중심대학공지',
        }
        return _KOREAN_NAMES.get(self.value, '알 수 없음')

    def get_collection_name(self) -> str:
        """MongoDB 컬렉션 이름을 반환합니다."""
        return self.value

    @classmethod
    def from_str(cls, value: str) -> Optional['ScrapperType']:
        """문자열로부터 ScrapperType을 생성합니다."""
        try:
            return cls(value)  # Enum의 value로 직접 생성
        except ValueError:
            return None

    @classmethod
    def get_choices(cls) -> list:
        """디스코드 명령어용 선택지 목록을 반환합니다."""
        return [
            app_commands.Choice(name=type.get_korean_name(), value=type.value)
            for type in cls
        ]