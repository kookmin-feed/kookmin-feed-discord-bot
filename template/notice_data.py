from dataclasses import dataclass
from datetime import datetime
from template.scrapper_type import ScrapperType

@dataclass
class NoticeData:
    """bs4,rss로 가져온 데이터를 표현하는 클래스"""
    title: str
    link: str
    published: datetime
    scrapper_type: ScrapperType

    def __str__(self):
        return (
            f"\n제목: {self.title}\n"
            f"구분: {self.scrapper_type.get_korean_name()}\n"
            f"작성일: {self.published.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"링크: {self.link}\n"
            f"{'-' * 80}"
        )