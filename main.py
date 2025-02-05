import asyncio
from discord_bot import client, send_notice
from rss_feed_checker import check_updates
from sw_notice_checker import start_monitoring
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

async def shutdown(rss_task, sw_task):
    """모든 태스크를 안전하게 종료합니다."""
    # 실행 중인 모든 태스크 취소
    rss_task.cancel()
    sw_task.cancel()
    
    # 태스크들이 완전히 종료될 때까지 대기
    try:
        await rss_task
    except asyncio.CancelledError:
        pass
    try:
        await sw_task
    except asyncio.CancelledError:
        pass

async def main():
    print("국민대학교 공지사항 알리미 봇을 시작합니다...")
    
    # RSS 피드 체커 태스크 생성
    print("RSS 피드 모니터링을 시작합니다...")
    RSS_URL = os.getenv('RSS_FEED_URL', 'https://cs.kookmin.ac.kr/news/notice/rss')
    rss_monitor_task = asyncio.create_task(check_updates(RSS_URL))
    
    # SW중심사업단 모니터링 태스크 생성
    print("SW중심사업단 모니터링을 시작합니다...")
    sw_monitor_task = asyncio.create_task(start_monitoring())
    
    print("디스코드 봇을 시작합니다...")
    try:
        await client.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 디스코드 봇 종료
        await client.close()
        # 모든 태스크 안전하게 종료
        await shutdown(rss_monitor_task, sw_monitor_task)
        # 이벤트 루프 정리
        await asyncio.get_event_loop().shutdown_asyncgens()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램이 안전하게 종료되었습니다.") 