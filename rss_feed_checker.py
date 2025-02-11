import os
import feedparser
import asyncio
from datetime import datetime
import pytz
from notice_entry import NoticeEntry
from discord_bot.crawler_manager import CrawlerType
from discord_bot.discord_bot import send_notice

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
    
    # 크롤러 타입에 따른 notice_type 매핑
    notice_type_map = {
        CrawlerType.ACADEMIC: 'academic',
        CrawlerType.SWACADEMIC: 'swAcademic',
        CrawlerType.SW: 'sw'
    }
    
    for entry in feed.entries:
        entry_data = {
            'title': entry.title,
            'link': entry.link,
            'published': parse_date(entry.published),
            'notice_type': notice_type_map.get(crawler_type, 'unknown')
        }
        entries.append(entry_data)
    
    return entries

def format_entry(entry):
    """피드 엔트리를 보기 좋은 형식으로 변환합니다."""
    try:
        # 한국 시간대로 변환
        kst = pytz.timezone('Asia/Seoul')
        
        # RSS 피드의 날짜 필드 찾기
        date_field = None
        for field in ['pubDate', 'published', 'updated']:
            if hasattr(entry, field):
                date_field = field
                break
                
        if date_field is None:
            raise ValueError("날짜 필드를 찾을 수 없습니다")
            
        # RSS 피드의 날짜 형식: 'Fri, 07 Feb 2025 16:07:41 +0900'
        published = datetime.strptime(getattr(entry, date_field), '%a, %d %b %Y %H:%M:%S %z')
        published_kst = published.astimezone(kst)
        
        return {
            'title': entry.title,
            'published': published_kst,
            'link': entry.link
        }
    except Exception as e:
        print(f"항목 형식 변환 중 오류 발생: {e}")
        print("엔트리 데이터:", entry)
        # 오류 발생시 1970년 1월 1일 사용 (작성일 표시 안됨)
        return {
            'title': entry.title,
            'published': datetime(1970, 1, 1, tzinfo=kst),
            'link': entry.link
        }

async def check_updates(url: str, crawler_type: CrawlerType = CrawlerType.SWACADEMIC):
    """RSS 피드를 주기적으로 확인하여 새로운 글이 있으면 디스코드로 전송합니다."""
    from discord_bot.discord_bot import send_notice
    
    last_entry = None
    while True:
        try:
            entries = parse_feed(url, crawler_type)
            if entries:
                notice = NoticeEntry(entries[0])
                
                # 새로운 공지사항인 경우에만 전송
                if last_entry != notice:
                    last_entry = notice
                    await send_notice(notice, crawler_type)
                    print(f"[{crawler_type.value}] 새로운 공지사항: {notice.title}")
                    
        except Exception as e:
            print(f"RSS 피드 확인 중 오류 발생: {e}")
            
        await asyncio.sleep(300)  # 5분마다 확인
