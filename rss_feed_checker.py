import os
import feedparser
from datetime import datetime
import pytz
from notice_entry import NoticeEntry
from discord_bot.crawler_manager import CrawlerType
from db_config import get_collection
from notice_type_map import NOTICE_TYPE_MAP

def parse_date(date_str):
    """날짜 문자열을 datetime 객체로 변환합니다."""
    try:
        dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        return dt
    except Exception as e:
        print(f"날짜 파싱 오류: {e}")
        return datetime.now(pytz.timezone('Asia/Seoul'))

def parse_feed(url, crawler_type: CrawlerType):
    """RSS 피드를 파싱하여 최신 글 목록을 반환합니다."""
    feed = feedparser.parse(url)
    entries = []
    
    for entry in feed.entries[:20]:  # 최근 20개만 가져오기
        entry_data = {
            'title': entry.title,
            'link': entry.link,
            'published': parse_date(entry.published),
            'notice_type': NOTICE_TYPE_MAP.get(crawler_type, 'unknown')
        }
        entries.append(entry_data)
    
    # 작성일 기준 오름차순 정렬
    entries.sort(key=lambda x: x['published'])
    return entries

async def check_updates(url: str, crawler_type: CrawlerType = CrawlerType.SWACADEMIC):
    """RSS 피드를 확인하여 새로운 글이 있으면 반환합니다."""
    try:
        # DB에서 해당 크롤러 타입의 최신 공지사항 가져오기
        collection = get_collection(NOTICE_TYPE_MAP[crawler_type])
        recent_notices = list(collection.find(
            sort=[('published', -1)]
        ).limit(20))
        
        # 제목으로 비교하기 위한 set
        recent_titles = {notice['title'] for notice in recent_notices}
        
        # 오늘 날짜 가져오기
        kst = pytz.timezone('Asia/Seoul')
        today = datetime.now(kst).date()
        
        entries = parse_feed(url, crawler_type)
        if not entries:
            return []

        new_notices = []
        for entry_data in entries:
            notice = NoticeEntry(entry_data)
            print(f"\n[크롤링된 공지] {notice.title}")
            
            # 오늘 작성된 공지사항이고, DB에 없는 새로운 공지사항인 경우
            if (notice.published.date() == today and 
                notice.title not in recent_titles):
                print("=> 새로운 공지사항입니다!")
                new_notices.append(notice)
                # DB에 저장
                collection.insert_one({
                    'title': notice.title,
                    'link': notice.link,
                    'published': notice.published.isoformat(),
                    'notice_type': notice.notice_type
                })
            else:
                if notice.published.date() != today:
                    print("=> 오늘 작성된 공지사항이 아닙니다")
                else:
                    print("=> 이미 등록된 공지사항입니다")

        return new_notices
                
    except Exception as e:
        print(f"RSS 피드 확인 중 오류 발생: {e}")
        return []
            
    
