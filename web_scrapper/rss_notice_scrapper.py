import os
import logging
import feedparser
from datetime import datetime
import pytz
from template.notice_data import NoticeData
from template.scrapper_type import ScrapperType
from config.db_config import get_collection
from web_scrapper.web_scrapper import WebScrapper
from bs4 import BeautifulSoup
from config.logger_config import setup_logger


class RSSNoticeScrapper(WebScrapper):
    def __init__(self, url: str, scrapper_type: ScrapperType = ScrapperType.SOFTWARE_NOTICE):
        """RSS 피드 스크래퍼를 초기화합니다.
        
        Args:
            url (str): RSS 피드 URL
            scraper_type (ScraperType, optional): 스크래퍼 타입. 기본값은 SWACADEMIC
        """
        super().__init__(url, scrapper_type)
        self.logger = setup_logger(self.scrapper_type.value)
    
    def parse_date(self, date_str):
        """날짜 문자열을 datetime 객체로 변환합니다."""
        try:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return dt
        except Exception as e:
            self.logger.error(f"날짜 파싱 오류: {e}")
            return datetime.now(self.kst)

    def get_list_elements(self, soup: BeautifulSoup) -> list:
        """RSS 피드에서는 사용하지 않습니다."""
        return []

    async def parse_notice_from_element(self, element) -> NoticeData:
        """RSS 피드에서는 사용하지 않습니다."""
        return None

    async def check_updates(self) -> list:
        """RSS 피드를 확인하여 새로운 글이 있으면 반환합니다."""
        try:
            # DB에서 해당 스크래퍼 타입의 최신 공지사항 가져오기
            collection = get_collection(self.scrapper_type.get_collection_name())
            recent_notices = list(collection.find(
                sort=[('published', -1)]
            ).limit(20))
            
            # 제목으로 비교하기 위한 set
            recent_titles = {notice['title'] for notice in recent_notices}
            
            # 오늘 날짜 가져오기
            today = datetime.now(self.kst).date()
            
            # RSS 피드 파싱
            feed = feedparser.parse(self.url)
            new_notices = []
            
            for entry in feed.entries[:20]:  # 최근 20개만 가져오기
                notice = NoticeData(
                    title=entry.title,
                    link=entry.link,
                    published=self.parse_date(entry.published),
                    scrapper_type=self.scrapper_type
                )
                
                self.logger.debug(f"[크롤링된 공지] {notice.title}")
                
                if ( notice.published.date() == today and
                    notice.title not in recent_titles):
                    self.logger.debug("=> 새로운 공지사항입니다!")
                    new_notices.append(notice)
                else:
                    if notice.published.date() != today:
                        self.logger.debug("=> 오늘 작성된 공지사항이 아닙니다")
                    else:
                        self.logger.debug("=> 이미 등록된 공지사항입니다")

            self.logger.info(f"총 {len(new_notices)}개의 새로운 공지사항")  
            return new_notices
                
        except Exception as e:
            self.logger.error(f"RSS 피드 확인 중 오류 발생: {e}")
            return [] 