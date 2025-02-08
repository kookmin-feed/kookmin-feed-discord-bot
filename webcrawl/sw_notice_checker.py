import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pytz
from notice_entry import NoticeEntry
import logging
import asyncio
import time
import json
import os
from crawler_manager import CrawlerType

class SWNoticeChecker:
    def __init__(self):
        self.url = os.getenv('SW_URL', 'https://software.kookmin.ac.kr/software/bulletin/notice.do')
        self.seen_entries = set()
        self.kst = pytz.timezone('Asia/Seoul')
        self.session = None
        self.HISTORY_FILE = 'webcrawl/sw_notice_history.json'
        self.load_history()
        
    def load_history(self):
        """저장된 크롤링 기록을 불러옵니다."""
        try:
            if os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    # JSON에서 불러온 데이터로 NoticeEntry 객체 생성
                    for entry in history:
                        notice = NoticeEntry({
                            'title': entry['title'],
                            'link': entry['link'],
                            'published': datetime.fromisoformat(entry['published']).replace(tzinfo=self.kst)
                        })
                        self.seen_entries.add(notice)
                print(f"크롤링 기록 {len(self.seen_entries)}개를 불러왔습니다.")
        except Exception as e:
            print(f"크롤링 기록 로드 중 오류 발생: {e}")
            self.seen_entries = set()

    def save_history(self):
        """크롤링 기록을 파일에 저장합니다."""
        try:
            # NoticeEntry 객체를 JSON 직렬화 가능한 형태로 변환
            history = []
            for notice in self.seen_entries:
                history.append({
                    'title': notice.title,
                    'link': notice.link,
                    'published': notice.published.isoformat()
                })
            
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            print(f"크롤링 기록 {len(history)}개를 저장했습니다.")
        except Exception as e:
            print(f"크롤링 기록 저장 중 오류 발생: {e}")

    async def check_new_notices(self):
        """새로운 공지사항을 확인합니다."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    html = await response.text()
                
            soup = BeautifulSoup(html, 'html.parser')
            notices = []
            
            print("\n=== SW중심대학 공지사항 크롤링 결과 ===")
            for row in soup.select('table tbody tr'):
                title_cell = row.select_one('.b-td-left')
                if title_cell:
                    title_elem = title_cell.select_one('.b-title-box a')
                    date = row.select_one('td:nth-child(6)').text.strip()
                    
                    if title_elem:
                        title = title_elem.text.strip()
                        href = title_elem.get('href', '')
                        article_no = href.split('articleNo=')[1].split('&')[0] if 'articleNo=' in href else ''
                        # 환경변수에서 기본 URL 가져오기
                        base_url = os.getenv('SW_URL', 'https://software.kookmin.ac.kr/software/bulletin/notice.do')
                        link = f"{base_url}?mode=view&articleNo={article_no}"
                        
                        entry = {
                            'title': title,
                            'link': link,
                            'published': self.parse_date(date)
                        }
                        
                        notice = NoticeEntry(entry)
                        print(f"\n[크롤링된 공지] {notice.title}")
                        
                        if notice not in self.seen_entries:
                            print("=> 새로운 공지사항입니다!")
                            notices.append(notice)
                            self.seen_entries.add(notice)
            
            return notices
            
        except Exception as e:
            logging.error(f"공지사항 확인 중 오류 발생: {str(e)}")
            return []

    def parse_date(self, date_str):
        """날짜 문자열을 datetime 객체로 변환합니다."""
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').replace(tzinfo=self.kst)
        except Exception as e:
            logging.error(f"날짜 파싱 오류: {e}")
            return datetime.now(self.kst)

async def check_updates(url: str, crawler_type: CrawlerType = CrawlerType.SW):
    """SW중심대학 공지사항을 주기적으로 확인합니다."""
    from discord_bot import send_notice
    
    checker = SWNoticeChecker()
    checker.url = url
    
    print(f"SW중심대학 공지사항 모니터링을 시작합니다.")
    print("-" * 80)

    try:
        while True:
            try:
                new_notices = await checker.check_new_notices()
                
                if new_notices:
                    for notice in new_notices:
                        await send_notice(notice, crawler_type)
                        print(f"[{crawler_type.value}] 새로운 공지사항: {notice.title}")

            except Exception as e:
                logging.error(f"모니터링 중 오류 발생: {str(e)}")
            
            await asyncio.sleep(300)
    finally:
        checker.save_history()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(check_updates()) 