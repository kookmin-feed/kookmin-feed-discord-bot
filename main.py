import asyncio
from discord_bot import client, send_notice
from rss_feed_checker import check_updates as check_swacademic_updates

from sw_notice_checker import check_updates as check_sw_updates
import os
from dotenv import load_dotenv
from crawler_manager import CrawlerType

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

async def main():
    print("국민대학교 공지사항 알리미 봇을 시작합니다...")
    
    # RSS 피드 체커 태스크 생성
    print("RSS 피드 모니터링을 시작합니다...") 
    SWACADEMIC_RSS_URL = os.getenv('SWACADEMIC_RSS_URL', 'https://cs.kookmin.ac.kr/news/notice/rss')
    SW_URL = os.getenv('SW_URL', 'https://software.kookmin.ac.kr/software/bulletin/notice.do')
    
    # 각 크롤러 타입별로 모니터링 태스크 생성
    swacademic_task = asyncio.create_task(check_swacademic_updates(SWACADEMIC_RSS_URL, CrawlerType.SWACADEMIC))
    sw_task = asyncio.create_task(check_sw_updates(SW_URL, CrawlerType.SW))

    print("디스코드 봇을 시작합니다...")
    try:
        await client.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        await client.close()
        await shutdown(swacademic_task, sw_task)
        await asyncio.get_event_loop().shutdown_asyncgens()



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램이 안전하게 종료되었습니다.") 