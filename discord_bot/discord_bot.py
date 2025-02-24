import discord
from discord import app_commands
from discord_bot.scrapper_manager import ScrapperConfig
from template.scrapper_type import ScrapperType
from template.notice_data import NoticeData
from config.logger_config import setup_logger

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
        self.scrapper_config = ScrapperConfig()

    async def setup_hook(self):
        """봇 시작시 실행되는 설정"""
        # commands 폴더의 모든 명령어 로드
        await self.load_commands()

    async def load_commands(self):
        """commands 폴더의 모든 명령어를 로드합니다."""
        from discord_bot.commands import register, test

        # 각 명령어 모듈 등록
        await register.setup(self)


client = NoticeBot()  # main.py에서 사용


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


async def send_notice(notice: NoticeData, scrapper_type: ScrapperType):
    """특정 스크래퍼의 공지사항을 해당하는 모든 채널에 전송합니다."""
    try:
        await client.wait_until_ready()

        channels = client.scrapper_config.get_channels_for_scrapper(scrapper_type)
        for channel_id in channels:
            try:
                channel = client.get_channel(int(channel_id))
                if not channel:
                    try:
                        user = await client.fetch_user(int(channel_id))
                        channel = user.dm_channel
                        if not channel:
                            channel = await user.create_dm()
                    except:
                        logger.warning(f"사용자 ID {channel_id}를 찾을 수 없습니다.")
                        continue

                if not isinstance(channel, discord.DMChannel):
                    permissions = channel.permissions_for(channel.guild.me)
                    if not permissions.send_messages or not permissions.embed_links:
                        logger.warning(
                            f"채널 [{channel.name}]에 메시지를 보낼 권한이 없습니다."
                        )
                        continue

                embed = discord.Embed(
                    title=notice.title, url=notice.link, color=discord.Color.blue()
                )

                # 공지사항 종류 표시
                embed.add_field(
                    name="구분", value=scrapper_type.get_korean_name(), inline=True
                )

                if notice.published.year > 1970:
                    embed.add_field(
                        name="작성일",
                        value=notice.published.strftime("%Y-%m-%d"),
                        inline=True,
                    )

                await channel.send(embed=embed)
                logger.info(
                    f'채널 [{getattr(channel, "name", "DM")}]에 공지사항을 전송했습니다: {notice.title}'
                )

            except discord.Forbidden:
                logger.warning(
                    f'채널 [{getattr(channel, "name", "DM")}]에 메시지를 보낼 권한이 없습니다.'
                )
            except discord.NotFound:
                logger.warning(f"채널 ID {channel_id}가 존재하지 않습니다.")
            except Exception as e:
                logger.error(f"채널 [{channel_id}] 메시지 전송 중 오류: {str(e)}")
    except Exception as e:
        logger.error(f"디스코드 메시지 전송 중 오류 발생: {e}")
