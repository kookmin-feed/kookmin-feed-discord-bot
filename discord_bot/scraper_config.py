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
        """채널에 스크래퍼를 등록합니다."""
        scraper_name = scraper_type.collection_name

        if channel_type == "direct-messages":
            existing_dm = await get_direct_message(user_id=channel_id)
            if existing_dm:
                return await update_direct_message(
                    user_id=channel_id,
                    scrapers=existing_dm["scrapers"] + [scraper_name],
                )
            else:
                return await create_direct_message(
                    user_id=channel_id, user_name=channel_name, scrapers=[scraper_name]
                )
        else:
            existing_server = await get_server_channel(channel_id=channel_id)
            if existing_server:
                return await update_server_channel(
                    channel_id=channel_id,
                    scrapers=existing_server["scrapers"] + [scraper_name],
                )
            else:
                return await create_server_channel(
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
