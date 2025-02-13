import asyncio
import logging
from discord_bot import client, send_notice
from rss_feed_checker import check_updates
from sw_notice_checker import start_monitoring
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

async def shutdown(cs_task, sw_task):
    """모든 태스크를 안전하게 종료합니다."""
    # 실행 중인 모든 태스크 취소
    cs_task.cancel()
    sw_task.cancel()
    
    # 태스크들이 완전히 종료될 때까지 대기
    try:
        await cs_task
    except asyncio.CancelledError:
        pass
    try:
        await sw_task
    except asyncio.CancelledError:
        pass

async def main():
    logging.info("국민대학교 공지사항 알리미 봇을 시작합니다...")
    
    # RSS 피드 체커 태스크 생성
    logging.info("RSS 피드 모니터링을 시작합니다...")
    CS_RSS_URL = os.getenv('CS_RSS_URL', 'https://cs.kookmin.ac.kr/news/notice/rss')
    cs_monitor_task = asyncio.create_task(check_updates(CS_RSS_URL))
    
    # SW중심사업단 모니터링 태스크 생성
    logging.info("SW중심사업단 모니터링을 시작합니다...")
    sw_monitor_task = asyncio.create_task(start_monitoring())
    
    logging.info("디스코드 봇을 시작합니다...")
    try:
        await client.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        logging.info("\n프로그램을 종료합니다...")
    except Exception as e:
        logging.error(f"오류 발생: {e}")
    finally:
        # 디스코드 봇 종료
        await client.close()
        # 모든 태스크 안전하게 종료
        await shutdown(cs_monitor_task, sw_monitor_task)
        # 이벤트 루프 정리
        await asyncio.get_event_loop().shutdown_asyncgens()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("프로그램이 안전하게 종료되었습니다.") 