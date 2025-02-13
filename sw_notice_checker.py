import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pytz
from notice_entry import NoticeEntry
import logging
import asyncio
import json
import os
from discord_bot import client, send_notice

class SWNoticeChecker:
    def __init__(self):
        self.url = "https://software.kookmin.ac.kr/software/bulletin/notice.do"
        self.seen_entries = set()
        self.kst = pytz.timezone('Asia/Seoul')
        self.session = None
        self.HISTORY_FILE = 'sw_notice_history.json'
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
                logging.info(f"크롤링 기록 {len(self.seen_entries)}개를 불러왔습니다.")
        except Exception as e:
            logging.error(f"크롤링 기록 로드 중 오류 발생: {e}")
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
            logging.info(f"크롤링 기록 {len(history)}개를 저장했습니다.")
        except Exception as e:
            logging.error(f"크롤링 기록 저장 중 오류 발생: {e}")

    async def check_new_notices(self):
        """새로운 공지사항을 확인합니다."""
        try:
            # 매 요청마다 새로운 세션 생성
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    html = await response.text()
                
            soup = BeautifulSoup(html, 'html.parser')
            notices = []
            
            # 테이블의 모든 행을 선택 (tr)
            for row in soup.select('table tbody tr'):
                # 번호/구분/제목/첨부/작성자/작성일/조회수 열 선택
                title_cell = row.select_one('.b-td-left')
                if title_cell:
                    title_elem = title_cell.select_one('.b-title-box a')
                    category = row.select_one('td:nth-child(2)').text.strip()
                    author = row.select_one('td:nth-child(5)').text.strip()
                    date = row.select_one('td:nth-child(6)').text.strip()
                    
                    if title_elem:
                        title = title_elem.text.strip()
                        # href 속성에서 파라미터 추출
                        href = title_elem.get('href', '')
                        article_no = href.split('articleNo=')[1].split('&')[0] if 'articleNo=' in href else ''
                        link = f"https://software.kookmin.ac.kr/software/bulletin/notice.do?mode=view&articleNo={article_no}"
                        
                        entry = {
                            'title': title,
                            'link': link,
                            'published': self.parse_date(date)
                        }
                        
                        notice = NoticeEntry(entry)
                        if notice not in self.seen_entries:
                            notices.append(notice)
                            self.seen_entries.add(notice)
            
            return notices
            
        except Exception as e:
            logging.error(f"[SW] 공지사항 확인 중 오류 발생: {str(e)}")
            logging.error(f"[SW] 상세 오류: {e}")
            return []

    def parse_date(self, date_str):
        """날짜 문자열을 datetime 객체로 변환합니다."""
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').replace(tzinfo=self.kst)
        except Exception as e:
            logging.error(f"[SW] 날짜 파싱 오류: {e}")
            return datetime.now(self.kst)

async def start_monitoring(interval_minutes=1):
    """주기적으로 공지사항을 확인하고 디스코드로 전송합니다."""
    checker = SWNoticeChecker()
    interval_seconds = interval_minutes * 60
    
    logging.info(f"[SW] SW중심사업단 공지사항 모니터링을 시작합니다. 확인 주기: {interval_seconds}초")

    try:
        while True:
            try:
                new_notices = await checker.check_new_notices()
                current_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
                
                if new_notices:
                    logging.info("[SW중심사업단 공지사항] 새로운 공지사항이 있습니다:")
                    
                    for notice in new_notices:
                        logging.info(str(notice))
                        if client.is_ready():
                            await send_notice(notice)
                else:
                    logging.info("[SW중심사업단 공지사항] - 새로운 공지사항이 없습니다.")

            except Exception as e:
                logging.error(f"모니터링 중 오류 발생: {str(e)}")
            
            await asyncio.sleep(interval_seconds)
    finally:
        # 프로그램 종료 시 기록 저장
        checker.save_history()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # 디버그를 위해 interval을 1분으로 설정
    asyncio.run(start_monitoring(interval_minutes=1)) 