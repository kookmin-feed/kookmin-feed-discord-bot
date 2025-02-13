import asyncio
import os
from dotenv import load_dotenv
from discord_bot.discord_bot import client, send_notice
from webcrawl.academic_notice_checker import AcademicNoticeCrawler
from webcrawl.sw_notice_checker import SWNoticeCrawler
from rss_feed_checker import check_updates as check_rss
from discord_bot.crawler_manager import CrawlerType
from db_config import get_database, close_database, save_notice
from notice_type_map import NOTICE_TYPE_MAP
from discord.ext import tasks

# .env 파일에서 환경 변수 로드
load_dotenv()

async def process_new_notices(notices, crawler_type):
    """새로운 공지사항을 처리합니다."""
    for notice in notices:
        # DB에 저장
        await save_notice(notice, crawler_type)
        # 디스코드로 전송
        await send_notice(notice, crawler_type)

@tasks.loop(minutes=5)  # 5분마다 실행
async def check_all_notices():
    """모든 크롤러를 실행하고 새로운 공지사항을 처리합니다."""
    try:
        # 학사공지 크롤러
        academic_url = os.getenv('ACADEMIC_URL')
        academic_crawler = AcademicNoticeCrawler(academic_url)
        academic_notices = await academic_crawler.check_updates()
        await process_new_notices(academic_notices, CrawlerType.ACADEMIC)
        
        # SW중심대학 크롤러
        sw_url = os.getenv('SW_URL')
        sw_crawler = SWNoticeCrawler(sw_url)
        sw_notices = await sw_crawler.check_updates()
        await process_new_notices(sw_notices, CrawlerType.SW)
        
        # RSS 피드 크롤러
        rss_url = os.getenv('SWACADEMIC_RSS_URL')
        rss_notices = await check_rss(rss_url)
        await process_new_notices(rss_notices, CrawlerType.SWACADEMIC)
            
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

@check_all_notices.before_loop
async def before_check():
    """크롤링 시작 전 봇이 준비될 때까지 대기"""
    await client.wait_until_ready()

async def main():
    """메인 함수"""
    print("국민대학교 공지사항 알리미 봇을 시작합니다...")
    
    try:
        # MongoDB 연결 초기화
        db = get_database()
        print("MongoDB 연결이 성공적으로 설정되었습니다.")
        
        # 크롤링 태스크 시작
        check_all_notices.start()
        print("크롤링 작업이 시작되었습니다.")
        
        print("디스코드 봇을 시작합니다...")
        await client.start(os.getenv('DISCORD_TOKEN'))
        
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        check_all_notices.cancel()
        await client.close()
        close_database()
        await asyncio.get_event_loop().shutdown_asyncgens()

if __name__ == "__main__":
    asyncio.run(main()) 