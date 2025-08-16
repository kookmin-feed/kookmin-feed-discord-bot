from typing import List
from config.logger_config import setup_logger
from template.scraper_type import ScraperType
from utils.discord_data_api import *

logger = setup_logger(__name__)


class ScraperConfig:
    """스크래퍼 설정을 관리하는 클래스"""

    def __init__(self):
        pass

    async def get_channels_for_scraper(self, scraper_type: ScraperType) -> list:
        """특정 스크래퍼에 등록된 채널 목록을 반환합니다."""
        channels = []

        # DM 채널 검색
        dm_channels = await get_all_direct_messages()
        for dm in dm_channels:
            if scraper_type.collection_name in dm["scrapers"]:
                channels.append(dm["_id"])

        # 서버 채널 검색
        server_channels = await get_all_server_channels()
        for server in server_channels:
            if scraper_type.collection_name in server["scrapers"]:
                channels.append(server["_id"])

        return channels

    async def add_scraper(
        self,
        channel_id: str,
        channel_name: str,
        channel_type: str,
        scraper_type: ScraperType,
        guild_name: str = None,
    ) -> bool:
        """
        Register a scraper for a channel, creating the channel record if needed.
        
        Adds the scraper identified by scraper_type.collection_name to the channel's
        scraper list. For direct messages, channel_type must be "direct-messages"; any
        other value is treated as a server channel. If the channel record exists the
        scraper name is appended (unless it is already present); if the channel record
        does not exist a new direct-message or server channel record is created with
        the scraper registered.
        
        Parameters:
            channel_id (str): ID of the target channel or DM user.
            channel_name (str): Display name of the channel or DM user.
            channel_type (str): "direct-messages" for DMs, otherwise treated as a server channel.
            scraper_type (ScraperType): Scraper descriptor; its `collection_name` is used as the scraper identifier.
            guild_name (str | None): Server/guild name when creating a new server channel (optional).
        
        Returns:
            bool: True if the scraper was added or the channel record was created; False if the scraper was already registered.
        """
        scraper_name = scraper_type.collection_name

        if channel_type == "direct-messages":
            existing_dm = await get_direct_message(user_id=channel_id)
            if existing_dm:
                if scraper_name in existing_dm["scrapers"]:
                    return False # 이미 존재하는 스크래퍼이므로 False 반환
                return await update_direct_message(
                    user_id=channel_id,
                    scrapers=existing_dm["scrapers"] + [scraper_name],
                )
            else:
                return await create_direct_message( # DM 사용자가 존재하지 않으면 생성
                    user_id=channel_id, user_name=channel_name, scrapers=[scraper_name]
                )
        else:
            existing_server = await get_server_channel(channel_id=channel_id)
            if existing_server:
                if scraper_name in existing_server["scrapers"]:
                    return False  # 이미 존재하는 스크래퍼이므로 False 반환
                return await update_server_channel(
                    channel_id=channel_id,
                    scrapers=existing_server["scrapers"] + [scraper_name],
                )
            else:
                return await create_server_channel( # 서버 채널이 존재하지 않으면 생성
                    guild_name=guild_name,
                    channel_name=channel_name,
                    channel_id=channel_id,
                    scrapers=[scraper_name],
                )

    async def remove_scraper(
        self, channel_id: str, channel_type: str, scraper_type: ScraperType
    ) -> bool:
        """채널에서 스크래퍼를 제거합니다."""
        scraper_name = scraper_type.collection_name

        if channel_type == "direct-messages":
            existing_dm = await get_direct_message(user_id=channel_id)
            if existing_dm:
                updated_scrapers = [
                    s for s in existing_dm["scrapers"] if s != scraper_name
                ]
                return await update_direct_message(
                    user_id=channel_id, scrapers=updated_scrapers
                )
        else:
            existing_server = await get_server_channel(channel_id=channel_id)
            if existing_server:
                updated_scrapers = [
                    s for s in existing_server["scrapers"] if s != scraper_name
                ]
                return await update_server_channel(
                    channel_id=channel_id, scrapers=updated_scrapers
                )

        return False

    async def get_channel_scrapers(
        self, channel_id: str, channel_type: str
    ) -> list[str]:
        """채널에 등록된 스크래퍼 목록을 반환합니다."""
        if channel_type == "direct-messages":
            existing_dm = await get_direct_message(user_id=channel_id)
            if existing_dm:
                return existing_dm["scrapers"]

        else:
            existing_server = await get_server_channel(channel_id=channel_id)
            if existing_server:
                return existing_server["scrapers"]

        return []
