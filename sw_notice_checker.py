import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from notice_entry import NoticeEntry
import logging
import asyncio
from discord_bot import client, send_notice

class SWNoticeChecker:
    def __init__(self):
        self.url = "https://software.kookmin.ac.kr/software/bulletin/notice.do"
        self.kst = pytz.timezone('Asia/Seoul')
        self.last_link = None

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
                        notices.append(NoticeEntry(entry))
            
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
        # 최초 실행시 현재 글 목록 가져오기
        current_notices = await checker.check_new_notices()
        if not current_notices:
            logging.warning("[SW] 공지사항을 가져올 수 없습니다.")
            return
            
        # 최초 실행시 마지막 글 링크 저장
        checker.last_link = current_notices[0].link
        # logging.info(f"[SW] 최초 실행: 마지막 글 제목 - {current_notices[0].title}")

        while True:
            try:
                current_notices = await checker.check_new_notices()
                current_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
                
                if current_notices and current_notices[0].link != checker.last_link:
                    # 새로운 글이 있는 경우
                    new_notices = []
                    for notice in current_notices:
                        if notice.link == checker.last_link:
                            break
                        new_notices.append(notice)

                    if new_notices:
                        logging.info("[SW] 새로운 공지사항이 있습니다:")
                        for notice in new_notices:
                            logging.info(f"[SW] {str(notice)}")
                            if client.is_ready():
                                await send_notice(notice)

                    checker.last_link = current_notices[0].link
                else:
                    logging.info("[SW] 새로운 공지사항이 없습니다.")

            except Exception as e:
                logging.error(f"[SW] 모니터링 중 오류 발생: {str(e)}")
            
            await asyncio.sleep(interval_seconds)

    except Exception as e:
        logging.error(f"[SW] 치명적인 오류 발생: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(start_monitoring(interval_minutes=1)) 