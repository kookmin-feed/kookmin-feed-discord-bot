import os
import feedparser
import asyncio
from datetime import datetime
import pytz
from notice_entry import NoticeEntry
from discord_bot import send_notice
import logging

def parse_feed(url):
    """RSS 피드를 파싱하여 최신 글 목록을 반환합니다."""
    feed = feedparser.parse(url)
    # 최초 실행시에만 디버깅 정보 출력
    if not hasattr(parse_feed, 'debug_shown') and feed.entries:
        logging.debug("[CS] 첫 번째 항목의 모든 필드 값:")
        first_entry = feed.entries[0]
        for key in first_entry.keys():
            logging.debug(f"[CS] [{key}]")
            logging.debug(f"[CS] {first_entry[key]}")
            logging.debug("[CS] " + "-" * 40)
        parse_feed.debug_shown = True
    return feed.entries

def format_entry(entry):
    """피드 엔트리를 보기 좋은 형식으로 변환합니다."""
    try:
        # 한국 시간대로 변환
        kst = pytz.timezone('Asia/Seoul')
        published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        published_kst = published.astimezone(kst)
        
        return {
            'title': entry.title,
            'published': published_kst,
            'link': entry.link
        }
    except Exception as e:
        logging.error(f"[CS] 항목 형식 변환 중 오류 발생: {e}")
        logging.error(f"[CS] 항목 데이터: {entry}")
        raise

async def check_updates(url, interval=60):
    """주기적으로 RSS 피드를 확인하고 업데이트를 출력합니다."""
    logging.info(f"[CS] 국민대학교 컴퓨터학부 공지사항 모니터링을 시작합니다. 확인 주기: {interval}초")

    last_entries = feedparser.parse(url).entries
    if not last_entries:
        logging.warning("[CS] 피드에서 항목을 찾을 수 없습니다.")
        return

    last_link = last_entries[0].link if last_entries else None

    while True:
        try:
            current_entries = feedparser.parse(url).entries
            current_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
            
            if current_entries and current_entries[0].link != last_link:
                # 새로운 글이 있는 경우
                new_entries = []
                for entry in current_entries:
                    if entry.link == last_link:
                        break
                    new_entries.append(format_entry(entry))

                if new_entries:
                    logging.info(f"[CS] 새로운 공지사항이 있습니다:")
                    for entry in new_entries:
                        notice = NoticeEntry(entry)
                        logging.info(f"[CS] {str(notice)}")
                        await send_notice(notice)

                last_link = current_entries[0].link
            else:
                logging.info(f"[CS] 새로운 공지사항이 없습니다.")

            await asyncio.sleep(interval)

        except Exception as e:
            logging.error(f"[CS] 오류 발생: {e}")
            logging.info("[CS] 계속 모니터링을 시도합니다...")
            await asyncio.sleep(interval)

async def start_monitoring():
    """RSS 피드 모니터링과 디스코드 봇을 동시에 실행합니다."""
    RSS_URL = os.getenv('RSS_FEED_URL', 'https://cs.kookmin.ac.kr/news/notice/rss')
    
    # RSS 피드 모니터링 시작
    await check_updates(RSS_URL)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(start_monitoring()) 