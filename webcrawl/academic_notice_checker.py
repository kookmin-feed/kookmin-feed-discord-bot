from bs4 import BeautifulSoup
from datetime import datetime
from notice_entry import NoticeEntry
from discord_bot.crawler_manager import CrawlerType
from notice_type_map import NOTICE_TYPE_MAP
from webcrawl.web_crawler import WebCrawler

class AcademicNoticeCrawler(WebCrawler):
    def __init__(self, url: str):
        super().__init__(url, CrawlerType.ACADEMIC)
    
    def get_list_elements(self, soup: BeautifulSoup) -> list:
        """학사공지 목록의 HTML 요소들을 가져옵니다."""
        return soup.select('.list-tbody .normal-bg, .list-tbody .notice-bg')
    
    async def parse_notice_from_element(self, row) -> NoticeEntry:
        """HTML 요소에서 학사공지 정보를 추출합니다."""
        try:
            title_tag = row.select_one('.subject a')
            if not title_tag:
                return None
                
            title = title_tag.text.strip()
            link = title_tag['href']
            if not link.startswith('http'):
                link = f"https://cs.kookmin.ac.kr/news/kookmin/academic/{link}"
            
            date = row.select_one('.date').text.strip()
            published = datetime.strptime(date, '%Y-%m-%d').replace(
                tzinfo=self.kst
            )
            
            return NoticeEntry({
                'title': title,
                'link': link,
                'published': published,
                'notice_type': NOTICE_TYPE_MAP[self.crawler_type]
            })
        except Exception as e:
            print(f"공지사항 파싱 중 오류: {e}")
            return None

async def check_updates(url: str, crawler_type: CrawlerType = CrawlerType.ACADEMIC):
    crawler = AcademicNoticeCrawler(url)
    return await crawler.check_updates() 