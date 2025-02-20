from __future__ import annotations

from abc import ABC, abstractmethod
import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from template.notice_data import NoticeData
from config.db_config import get_collection
from config.logger_config import setup_logger
from template.scrapper_type import ScrapperType
from typing import List



class WebScrapper(ABC):
    """웹 스크래퍼의 기본 클래스"""
    def __init__(self, url: str, scrapper_type: ScrapperType):
        self.url = url
        self.scrapper_type = scrapper_type
        self.kst = pytz.timezone('Asia/Seoul')
        self.logger = setup_logger(self.scrapper_type.get_collection_name())
        
    async def check_updates(self) -> List[NoticeData]:
        """웹페이지를 확인하여 새로운 공지사항이 있으면 반환합니다."""
        try:
            # DB에서 해당 크롤러 타입의 최신 공지사항 가져오기
            collection = get_collection(self.scrapper_type.get_collection_name())
            recent_notices = list(collection.find(
                sort=[('published', -1)]
            ).limit(50))
            
            # 제목으로 비교하기 위한 set
            recent_titles = {notice['title'] for notice in recent_notices}
            
            # 오늘 날짜 가져오기
            today = datetime.now(self.kst).date()
            
            # 웹페이지 가져오기
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    html = await response.text()
                    
            # HTML 파싱
            soup = BeautifulSoup(html, 'html.parser')
            elements = self.get_list_elements(soup)
            
            new_notices = []
            for element in elements:
                notice = await self.parse_notice_from_element(element)
                if notice:
                    self.logger.debug(f"[크롤링된 공지] {notice.title}")
                    
                    # 오늘 작성된 공지사항이고, DB에 없는 새로운 공지사항인 경우
                    
                    if ( notice.title not in recent_titles):
                        self.logger.debug("=> 새로운 공지사항입니다!")
                        new_notices.append(notice)
                    else:
                        self.logger.debug("=> 이미 등록된 공지사항입니다")
            
            self.logger.info(f"총 {len(new_notices)}개의 새로운 공지사항")
            return new_notices
            
        except Exception as e:
            self.logger.error(f"공지사항 확인 중 오류 발생: {e}")
            return []
    
    @abstractmethod
    async def parse_notice_from_element(self, element) -> NoticeData:
        """HTML 요소에서 공지사항 정보를 추출합니다."""
        pass
    
    @abstractmethod
    def get_list_elements(self, soup: BeautifulSoup) -> list:
        """공지사항 목록의 HTML 요소들을 가져옵니다."""
        pass 