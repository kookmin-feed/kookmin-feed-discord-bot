from bs4 import BeautifulSoup
from datetime import datetime
from notice_entry import NoticeEntry
from discord_bot.crawler_manager import CrawlerType
from notice_type_map import NOTICE_TYPE_MAP
from webcrawl.web_crawler import WebCrawler

class SWNoticeCrawler(WebCrawler):
    def __init__(self, url: str):
        super().__init__(url, CrawlerType.SW)
    
    def get_list_elements(self, soup: BeautifulSoup) -> list:
        """SW중심대학 공지사항 목록의 HTML 요소들을 가져옵니다."""
        return soup.select('table tbody tr')
    
    async def parse_notice_from_element(self, row) -> NoticeEntry:
        """HTML 요소에서 SW중심대학 공지사항 정보를 추출합니다."""
        try:
            title_cell = row.select_one('.b-td-left')
            if not title_cell:
                return None
                
            title_elem = title_cell.select_one('.b-title-box a')
            if not title_elem:
                return None
                
            title = title_elem.text.strip()
            href = title_elem.get('href', '')
            article_no = href.split('articleNo=')[1].split('&')[0] if 'articleNo=' in href else ''
            link = f"{self.url}?mode=view&articleNo={article_no}"
            
            date = row.select_one('td:nth-child(6)').text.strip()
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

async def check_updates(url: str, crawler_type: CrawlerType = CrawlerType.SW):
    crawler = SWNoticeCrawler(url)
    return await crawler.check_updates()