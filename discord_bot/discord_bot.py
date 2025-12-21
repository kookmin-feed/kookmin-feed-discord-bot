from pathlib import Path
import sys
import asyncio
from datetime import datetime

# # 프로젝트 루트를 sys.path에 추가
# project_root = Path(__file__).parent.parent
# if str(project_root) not in sys.path:
#     sys.path.insert(0, str(project_root))
#       uv run python discord_bot/discord_bot.py 로 테스트 할 수 있는 테스트 코드

import discord
from discord import app_commands
from discord_bot.scraper_config import ScraperConfig
from template.scraper_type import ScraperType
from template.notice_data import NoticeData
from config.logger_config import setup_logger
from config.env_loader import (
    ENV,
)  # db_config에서 가져오는 대신 직접 env_loader에서 가져옴
from utils.discord_data_api import create_server_channel

logger = setup_logger(__name__)

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.guilds = True  # 서버 목록 확인용
intents.dm_messages = True  # DM 메시지 허용


class NoticeBot(discord.Client):  # discord.Client 클래스를 상속받음
    def __init__(self):
        # intents 봇이 어떤 이벤트를 받을 수 있는지 지정
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.scraper_config = ScraperConfig()

    async def setup_hook(self):
        """봇 시작시 실행되는 설정"""
        # commands 폴더의 모든 명령어 로드
        await self.load_commands()

    async def load_commands(self):
        """commands 폴더의 모든 명령어를 로드합니다."""
        from discord_bot.commands import register, test

        # 각 명령어 모듈 등록
        await register.setup(self)

        if not ENV["IS_PROD"]:  # IS_PROD 대신 ENV["IS_PROD"] 사용
            await test.setup(self)


client = NoticeBot()  # main.py에서 사용


@client.event
async def on_ready():
    """봇이 시작될 때 실행되는 이벤트"""
    logger.debug(f"봇이 시작되었습니다: {client.user.name}")

    try:
        logger.debug("슬래시 커맨드를 전역으로 등록합니다...")
        await client.tree.sync()
        logger.debug("슬래시 커맨드 등록이 완료되었습니다.")
    except Exception as e:
        logger.error(f"슬래시 커맨드 등록 중 오류 발생: {e}")

    logger.debug("봇이 준비되었습니다!")


@client.event
async def on_guild_join(guild):
    """봇이 새로운 서버에 참여했을 때 실행됩니다."""
    logger.info(f"새로운 서버 [{guild.name}]에 참여했습니다.")
    try:
        await client.tree.sync(guild=guild)
        logger.info(f"서버 [{guild.name}]에 슬래시 커맨드를 등록했습니다.")
    except Exception as e:
        logger.error(f"서버 [{guild.name}]에 슬래시 커맨드 등록 실패: {e}")


async def send_notice(notice: NoticeData, scraper_type: ScraperType):
    """특정 스크래퍼의 공지사항을 해당하는 모든 채널에 전송합니다."""
    try:
        await client.wait_until_ready()

        channels = await client.scraper_config.get_channels_for_scraper(scraper_type)
        for channel_id in channels:
            channel = None  # Initialize channel to avoid NameError
            try:
                # 먼저 유저 ID로 시도
                try:
                    user = await client.fetch_user(int(channel_id))
                    channel = user.dm_channel
                    if channel is None:
                        channel = await user.create_dm()

                except discord.NotFound:
                    # 유저를 찾을 수 없으면 채널 ID일 가능성이 있으므로 채널로 시도
                    channel = await client.fetch_channel(int(channel_id))

                embed = discord.Embed(
                    title=notice.title, url=notice.link, color=discord.Color.blue()
                )

                # 공지사항 종류 표시
                embed.add_field(
                    name="구분", value=scraper_type.korean_name, inline=True
                )

                if notice.published.year > 1970:
                    embed.add_field(
                        name="작성일",
                        value=notice.published.strftime("%Y-%m-%d"),
                        inline=True,
                    )

                await channel.send(embed=embed)

                # except가 발생하지 않았을 때만 로그 출력
                if channel is not None:
                    if isinstance(channel, discord.DMChannel):
                        channel_name = getattr(
                            channel.recipient, "name", "channel is None"
                        )
                        logger.info(
                            f"DM 채널 [{channel_name}]에 공지사항을 전송했습니다: {notice.title}"
                        )
                    elif hasattr(channel, "guild"):
                        channel_name = getattr(channel, "name", "channel is None")
                        logger.info(
                            f"채널 [{channel_name}]에 공지사항을 전송했습니다: {notice.title}"
                        )
                    else:
                        logger.error(
                            f"채널 {channel_id}: 알 수 없는 채널 타입 {type(channel)}"
                        )

            except discord.Forbidden as e:
                if channel is not None and isinstance(channel, discord.DMChannel):
                    logger.error(
                        f"[{scraper_type.korean_name}] {channel_id} 유저: {channel.recipient} 에 메세지를 보낼 권한이 없습니다."
                    )
                else:
                    logger.error(
                        f"[{scraper_type.korean_name}] 채널: {channel_id} 채널 권한 오류: {str(e)}"
                    )
            except discord.NotFound as e:
                # 이미 내부에서 처리했지만, 다른 경우를 대비한 예외 처리
                logger.error(
                    f"채널/유저 ID {channel_id}를 찾을 수 없습니다. 오류: {str(e)}"
                )
            except Exception as e:
                logger.error(f"채널 [{channel_id}] 메시지 전송 중 오류: {str(e)}")

    except Exception as e:
        logger.error(f"디스코드 메시지 전송 중 오류 발생: {e}")


# async def main():
#     """메인 비동기 함수
#       uv run python discord_bot/discord_bot.py 로 테스트 할 수 있는 테스트 코드
# """
#     id_list = ["360697010581536768"]

#     # 봇을 백그라운드에서 시작
#     async def start_bot():
#         try:
#             await client.start(ENV["DISCORD_TOKEN"])
#         except Exception as e:
#             logger.error(f"봇 시작 중 오류 발생: {e}")

#     # 봇 시작 태스크 생성
#     bot_task = asyncio.create_task(start_bot())

#     # 태스크가 시작되고 클라이언트가 초기화될 시간을 줍니다
#     await asyncio.sleep(1)

#     try:
#         # 봇이 준비될 때까지 대기
#         await client.wait_until_ready()
#         logger.info("봇이 준비되었습니다. 권한 체크를 시작합니다.")

#         # 임시 데이터 생성
#         scraper_type = ScraperType(
#             korean_name="대학 학사공지",
#             scraper_colloction_name="university_academic",
#             scraper_type_name="UNIVERSITY_ACADEMIC",
#         )
#         notice_data = NoticeData(
#             title="테스트 공지사항",
#             link="https://cs.kookmin.ac.kr/news/kookmin/academic/",
#             published=datetime.now(),
#             scraper_type=scraper_type,
#         )

#         # 권한 체크 수행
#         try:
#             for id in id_list:
#                 await send_notice(notice_data, scraper_type)

#         except Exception as e:
#             logger.error(f"채널 권한 체크 중 오류 발생: {e}")

#         # 봇이 계속 실행되도록 대기
#         await bot_task
#     except Exception as e:
#         logger.error(f"봇 실행 중 오류 발생: {e}")
#         raise


# if __name__ == "__main__":
#     asyncio.run(main())
