from abc import ABC, abstractmethod
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from notice_entry import NoticeEntry
import logging
from db_config import get_collection
from notice_type_map import NOTICE_TYPE_MAP

class WebCrawler(ABC):
    def __init__(self, url: str, crawler_type):
        self.url = url
        self.crawler_type = crawler_type
        self.kst = pytz.timezone('Asia/Seoul')
        
    @abstractmethod
    async def parse_notice_from_element(self, element) -> NoticeEntry:
        """HTML 요소에서 공지사항 정보를 추출합니다."""
        pass
    
    @abstractmethod
    def get_list_elements(self, soup: BeautifulSoup) -> list:
        """공지사항 목록의 HTML 요소들을 가져옵니다."""
        pass
        
    async def check_updates(self):
        """웹 페이지를 확인하여 새로운 글이 있으면 반환합니다."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    notices = []
                    
                    # 최근 20개의 DB 공지사항 가져오기
                    collection = get_collection(NOTICE_TYPE_MAP[self.crawler_type])
                    recent_notices = list(collection.find(
                        sort=[('published', -1)]
                    ).limit(20))
                    
                    # 제목으로 비교하기 위한 set
                    recent_titles = {notice['title'] for notice in recent_notices}
                    
                    # 오늘 날짜 가져오기
                    today = datetime.now(self.kst).date()
                    
                    # 공지사항 목록 파싱
                    for element in self.get_list_elements(soup):
                        try:
                            notice = await self.parse_notice_from_element(element)
                            if notice:
                                print(f"\n[크롤링된 공지] {notice.title}")
                                
                                # 오늘 작성된 공지사항이고, DB에 없는 새로운 공지사항인 경우
                                if (notice.published.date() == today and 
                                    notice.title not in recent_titles):
                                    print("=> 새로운 공지사항입니다!")
                                    notices.append(notice)
                                else:
                                    if notice.published.date() != today:
                                        print("=> 오늘 작성된 공지사항이 아닙니다")
                                    else:
                                        print("=> 이미 등록된 공지사항입니다")
                        
                        except Exception as e:
                            print(f"공지사항 파싱 중 오류: {e}")
                            continue
                    
                    return notices
                    
        except Exception as e:
            logging.error(f"공지사항 확인 중 오류 발생: {str(e)}")
            return [] 