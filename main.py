import asyncio
import os
from dotenv import load_dotenv
from discord_bot.discord_bot import client
from rss_feed_checker import check_updates as check_rss_swacademic_updates
from webcrawl.academic_notice_checker import check_updates as check_academic_updates
from webcrawl.sw_notice_checker import check_updates as check_sw_updates
from discord_bot.crawler_manager import CrawlerType
from db_config import get_database, close_database

# .env 파일에서 환경 변수 로드
load_dotenv()

async def shutdown(academic_task, office_task, sw_task):
    """모든 태스크를 안전하게 종료합니다."""
    for task in [academic_task, office_task, sw_task]:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    # MongoDB 연결 종료
    close_database()

async def main():
    print("국민대학교 공지사항 알리미 봇을 시작합니다...")
    
    # MongoDB 연결 초기화
    try:
        db = get_database()
        print("MongoDB 연결이 성공적으로 설정되었습니다.")
    except Exception as e:
        print(f"MongoDB 연결 중 오류 발생: {e}")
        return

    # RSS 피드 체커 태스크 생성
    print("RSS 피드 모니터링을 시작합니다...") 
    SWACADEMIC_RSS_URL = os.getenv('SWACADEMIC_RSS_URL', 'https://cs.kookmin.ac.kr/news/notice/rss')
    SW_URL = os.getenv('SW_URL', 'https://software.kookmin.ac.kr/software/bulletin/notice.do')
    ACADEMIC_URL = os.getenv('ACADEMIC_URL', 'https://cs.kookmin.ac.kr/news/kookmin/academic/')
    
    # 각 크롤러 타입별로 모니터링 태스크 생성
    swacademic_task = asyncio.create_task(check_rss_swacademic_updates(SWACADEMIC_RSS_URL, CrawlerType.SWACADEMIC))
    sw_task = asyncio.create_task(check_sw_updates(SW_URL, CrawlerType.SW))
    academic_task = asyncio.create_task(check_academic_updates(ACADEMIC_URL, CrawlerType.ACADEMIC))

    print("디스코드 봇을 시작합니다...")
    try:
        await client.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        await client.close()
        await shutdown(swacademic_task, sw_task, academic_task)
        await asyncio.get_event_loop().shutdown_asyncgens()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램이 안전하게 종료되었습니다.") 