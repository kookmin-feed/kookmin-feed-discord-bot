import asyncio
import sys
import os
from datetime import datetime
import pytz
from discord_bot.discord_bot import client, send_notice
from utils.scrapper_type import ScrapperType
from discord.ext import tasks
from config.logger_config import setup_logger
from config.db_config import get_database, close_database, save_notice
from utils.scrapper_factory import ScrapperFactory
from config.env_loader import ENV


if ENV["IS_PROD"]:
    INTERVAL = 10
else:
    INTERVAL = 2

print(f"INTERVAL: {INTERVAL}")


async def process_new_notices(notices, scrapper_type: ScrapperType):
    """새로운 공지사항을 처리합니다."""
    for notice in notices:
        # DB에 저장
        await save_notice(notice, scrapper_type)
        # 디스코드로 전송
        await send_notice(notice, scrapper_type)


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
async def check_all_notices():
    """모든 스크래퍼를 실행하고 새로운 공지사항을 처리합니다."""
    try:
        # 작동 시간이 아니면 스킵
        if not is_working_hour():
            current_time = datetime.now(pytz.timezone("Asia/Seoul")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            logger.info(f"작동 시간이 아닙니다. (현재 시각: {current_time})")
            return
        # 활성화된 모든 스크래퍼 실행
        for scrapper_type in ScrapperType.get_active_scrappers():
            try:
                # 스크래퍼 생성
                scrapper = ScrapperFactory().create_scrapper(scrapper_type)
                if not scrapper:
                    logger.error(f"지원하지 않는 스크래퍼 타입: {scrapper_type.name}")
                    continue

                # 공지사항 확인 및 처리
                notices = await scrapper.check_updates()
                await process_new_notices(notices, scrapper_type)

            except Exception as e:
                logger.error(
                    f"{scrapper_type.get_korean_name()} 스크래핑 중 오류 발생: {e}"
                )
                continue

    except Exception as e:
        logger.error(f"스크래핑 작업 중 오류 발생: {e}")


@check_all_notices.before_loop
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

        # MongoDB 연결 초기화
        db = get_database()
        logger.info("MongoDB 연결이 성공적으로 설정되었습니다.")

        # 크롤링 태스크 시작
        check_all_notices.start()
        logger.info("크롤링 작업이 시작되었습니다.")

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
        check_all_notices.cancel()
        await client.close()
        close_database()
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
