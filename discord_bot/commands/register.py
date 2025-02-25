from discord import app_commands
import discord
from utils.scrapper_type import ScrapperType
from typing import Literal
from config.logger_config import setup_logger

logger = setup_logger(__name__)


async def setup(bot):
    """공지 등록/삭제 관련 명령어들을 봇에 등록합니다."""

    @bot.tree.command(name="게시판_선택", description="알림을 받을 게시판을 선택합니다")
    @app_commands.describe(scrapper="게시판 종류")
    @app_commands.choices(scrapper=ScrapperType.get_choices())
    async def register_notice(interaction: discord.Interaction, scrapper: str):
        """공지사항 알림을 등록합니다."""
        try:
            scrapper_type = ScrapperType.from_str(scrapper)
            if not scrapper_type:
                await interaction.response.send_message(
                    "올바르지 않은 게시판 입니다.", ephemeral=True
                )
                return

            # DM인지 서버 채널인지 확인
            if isinstance(interaction.channel, discord.DMChannel):
                channel_id = str(interaction.user.id)
                channel_type = "DM"
                logger.info(f"DM에서 등록: 사용자 ID {channel_id}")
            else:
                # 서버 채널인 경우 관리자 권한 확인
                if not interaction.permissions.administrator:
                    await interaction.response.send_message(
                        "이 명령어는 관리자 권한이 필요합니다.", ephemeral=True
                    )
                    return
                channel_id = str(interaction.channel_id)
                channel_type = f"채널 #{interaction.channel.name}"
                logger.info(f"서버 채널에서 등록: 채널 ID {channel_id}")

            if interaction.client.scrapper_config.add_scrapper(
                channel_id, scrapper_type
            ):
                await interaction.response.send_message(
                    f"✅ 이 {channel_type}을(를) {scrapper_type.get_korean_name()} 알림을 받을 채널로 등록했습니다."
                )
            else:
                await interaction.response.send_message(
                    f"❗ 이미 이 {channel_type}은(는) {scrapper_type.get_korean_name()} 알림을 받도록 등록되어 있습니다."
                )
        except Exception as e:
            logger.error(f"알림 등록 중 오류 발생: {e}")
            await interaction.response.send_message(
                "알림 등록 중 오류가 발생했습니다.", ephemeral=True
            )

    @bot.tree.command(
        name="게시판_선택취소", description="선택한 게시판의 알림을 취소합니다"
    )
    @app_commands.describe(type="게시판 종류")
    @app_commands.choices(type=ScrapperType.get_choices())
    async def unregister_notice(interaction: discord.Interaction, type: str):
        """현재 채널에서 선택한 유형의 공지사항 알림을 삭제합니다."""
        try:
            # DM에서 실행된 경우 사용자 ID를 사용
            if isinstance(interaction.channel, discord.DMChannel):
                channel_id = str(interaction.user.id)
                channel_type = "DM"
                logger.info(f"DM 채널에서 삭제: 사용자 ID {channel_id}")
            else:
                # 서버 채널인 경우 관리자 권한 확인
                if not interaction.permissions.administrator:
                    await interaction.response.send_message(
                        "이 명령어는 관리자 권한이 필요합니다.", ephemeral=True
                    )
                    return
                channel_id = str(interaction.channel_id)
                channel_type = f"채널 #{interaction.channel.name}"
                logger.info(f"서버 채널에서 삭제: 채널 ID {channel_id}")

            scrapper_type = ScrapperType.from_str(type)
            if not scrapper_type:
                await interaction.response.send_message(
                    "올바르지 않은 스크래퍼 타입입니다.", ephemeral=True
                )
                return

            if interaction.client.scrapper_config.remove_scrapper(
                channel_id, scrapper_type
            ):
                message = f"✅ 이 {channel_type}에서 {scrapper_type.get_korean_name()} 알림이 삭제되었습니다."
            else:
                message = f"❗ 이 {channel_type}에는 {scrapper_type.get_korean_name()} 알림이 등록되어 있지 않습니다."

            await interaction.response.send_message(message, ephemeral=True)

        except Exception as e:
            logger.error(f"알림 삭제 중 오류 발생: {e}")
            await interaction.response.send_message(
                "알림 삭제 중 오류가 발생했습니다.", ephemeral=True
            )

    @bot.tree.command(
        name="선택된_게시판", description="현재 선택된 게시판 목록을 보여줍니다"
    )
    async def list_crawlers(interaction: discord.Interaction):
        """현재 채널에 등록된 공지사항 알림 목록을 보여줍니다."""
        try:
            # DM인지 서버 채널인지 확인
            if isinstance(interaction.channel, discord.DMChannel):
                channel_id = str(interaction.user.id)
                channel_type = "DM"
                logger.info(f"DM에서 목록 조회: 사용자 ID {channel_id}")
            else:
                channel_id = str(interaction.channel_id)
                channel_type = f"채널 #{interaction.channel.name}"
                logger.info(f"서버 채널에서 목록 조회: 채널 ID {channel_id}")

            # 등록된 스크래퍼 목록 가져오기
            scrapper_type_list = (
                interaction.client.scrapper_config.get_channel_scrappers(channel_id)
            )

            if scrapper_type_list:
                # 등록된 스크래퍼 목록을 한글명으로 변환
                scrapper_names = [
                    f"- {ScrapperType.from_str(scrapper_type).get_korean_name()}"
                    for scrapper_type in scrapper_type_list
                ]
                message = f"**현재 {channel_type}에 등록된 알림:**\n" + "\n".join(
                    scrapper_names
                )
            else:
                message = f"현재 {channel_type}에 등록된 알림이 없습니다."

            await interaction.response.send_message(message, ephemeral=True)

        except Exception as e:
            logger.error(f"알림 목록 조회 중 오류 발생: {e}")
            await interaction.response.send_message(
                "알림 목록 조회 중 오류가 발생했습니다.", ephemeral=True
            )
