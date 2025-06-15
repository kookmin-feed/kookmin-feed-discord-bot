import asyncio
import sys
from datetime import datetime
import pytz
from discord_bot.discord_bot import client, send_notice
from discord.ext import tasks
from config.logger_config import setup_logger
from config.env_loader import ENV
from utils.data_server_conect import get_data_from_server
from utils.enum_data_api import *
from utils.scraper_data_api import *
from template.scraper_type_list import MetaData
from utils.notice_cache import LastNoticeData
from template.notice_data import NoticeData


# if ENV["IS_PROD"]:
#     INTERVAL = 10
# else:
#     INTERVAL = 2

INTERVAL = 20

print(f"INTERVAL: {INTERVAL}")

def is_working_hour():
    """현재 시간이 작동 시간(월~토 8시~20시)인지 확인합니다."""
    if not ENV["IS_PROD"]:
        return True

    now = datetime.now(pytz.timezone("Asia/Seoul"))

    # 일요일(6) 체크
    if now.weekday() == 6:
        return False

    # 시간 체크 (8시~20시)
    if now.hour < 8 or now.hour >= 21:
        return False

    return True


@tasks.loop(minutes=INTERVAL)
async def check_all_notice():
    """새로운 ENUM이 있는지 확인합니다. 
    새로운 공지가 있다면 메세지를 보냅니다."""
    
    try:
        # 작동 시간이 아니면 스킵
        if not is_working_hour():
            current_time = datetime.now(pytz.timezone("Asia/Seoul")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            logger.info(f"작동 시간이 아닙니다. (현재 시각: {current_time})")
            return

        logger.info("새로운 카테고리의 유무를 확인합니다...")
        MetaData.category_list = await get_all_categories()
        logger.info("새로운 스크래퍼 타입의 유무를 확인합니다...")
        MetaData.scraper_type_list = await get_all_scraper_types()
        
        for scraper_type in MetaData.scraper_type_list:
            type_name = scraper_type.collection_name
            
            # 최초 실행 또는 새로운 타입일 경우 메시지를 보내지 않고 최근 공지 캐싱
            if LastNoticeData.links.get(type_name) == None:
                logger.info(f"\"{scraper_type.name}\"의 캐시가 없습니다. 마지막 정보를 캐싱합니다.")
                
                last_notice = (await get_all_notices(type_name, 1))[0]
                LastNoticeData.links[type_name] = last_notice.link

                logger.info(f"\"{scraper_type.name}\"의 마지막 게시물 \"{last_notice.title}\"를 캐싱했습니다.")
            
            # 캐싱한 마지막 공지 기준으로 새로운 공지 발견시 메시지 보내기
            else:
                logger.info(f"\"{scraper_type.name}\"의 새 게시물을 가져옵니다...")
                new_notice_list = await get_new_notices(type_name, LastNoticeData.links[type_name])
                
                logger.info(f"\"{scraper_type.name}\"의 새 게시물은 {len(new_notice_list)}개 입니다.")
                
                for new_notice in reversed(new_notice_list):
                    await send_notice(new_notice, scraper_type)

                if len(new_notice_list) != 0:
                    LastNoticeData.links[type_name] = new_notice_list[0].link
                    logger.info(f"\"{scraper_type.name}\"의 마지막 게시물 \"{new_notice_list[0].title}\"를 캐싱했습니다.")

    except Exception as e:
        logger.error(f"API 호출 테스크 중 오류: {e}")


@check_all_notice.before_loop
async def before_check():
    """크롤링 시작 전 봇이 준비될 때까지 대기"""
    await client.wait_until_ready()


async def main():
    logger.info("국민대학교 공지사항 알리미 봇을 시작합니다...")

    try:
        # 환경 변수 검증
        discord_token = ENV["DISCORD_TOKEN"]
        if not discord_token:
            raise ValueError(
                "DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인해주세요."
            )

        # data server connection 테스트
        logger.info("Data Server 연결 상태를 검사합니다...")
        await get_data_from_server(endpoint="connect-check")

        logger.info("meta data를 초기화합니다.")
        
        MetaData.category_list = await get_all_categories()
        logger.info("카테고리 meta data 초기화 완료.")

        MetaData.scraper_type_list = await get_all_scraper_types()
        logger.info("스크래퍼 타입 meta data를 초기화 완료.")

        logger.info("kookmin-feed API 호출 테스크를 시작합니다...")
        check_all_notice.start()
        logger.info("kookmin-feed API 호출 테스크가 정상적으로 시작되었습니다.")

        logger.info("디스코드 봇을 시작합니다...")
        await client.start(discord_token)

    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n프로그램을 종료합니다...")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
    finally:
        check_all_notice.cancel()
        await client.close()
        await asyncio.get_event_loop().shutdown_asyncgens()


@client.event
async def on_ready():
    """봇이 시작될 때 실행되는 이벤트"""
    logger.info(f"봇이 시작되었습니다: {client.user.name}")

    try:
        logger.info("슬래시 커맨드를 전역으로 등록합니다...")
        await client.tree.sync()
        logger.info("슬래시 커맨드 등록이 완료되었습니다.")
    except Exception as e:
        logger.error(f"슬래시 커맨드 등록 중 오류 발생: {e}")

    logger.info("봇이 준비되었습니다!")


@client.event
async def on_guild_join(guild):
    """봇이 새로운 서버에 참여했을 때 실행됩니다."""
    logger.info(f"새로운 서버 [{guild.name}]에 참여했습니다.")
    try:
        await client.tree.sync(guild=guild)
        logger.info(f"서버 [{guild.name}]에 슬래시 커맨드를 등록했습니다.")
    except Exception as e:
        logger.error(f"서버 [{guild.name}]에 슬래시 커맨드 등록 실패: {e}")


if __name__ == "__main__":

    logger = setup_logger(__name__)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("프로그램이 안전하게 종료되었습니다.")
