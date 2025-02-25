from typing import List
from config.db_config import get_database
from config.logger_config import setup_logger
from utils.scrapper_type import ScrapperType

logger = setup_logger(__name__)


class ScrapperConfig:
    """스크래퍼 설정을 관리하는 클래스"""

    def __init__(self):
        self.db = get_database(db_name="notification-recipient")
        self.dm_collection = self.db["direct-messages"]
        self.server_channel_collection = self.db["server-channels"]

    def get_channels_for_scrapper(self, scrapper_type: ScrapperType) -> list:
        """특정 스크래퍼에 등록된 채널 목록을 반환합니다."""
        channels = []

        # DM 채널 검색
        dm_cursor = self.db["direct-messages"].find(
            {"scrappers": scrapper_type.get_collection_name()}
        )
        for doc in dm_cursor:
            channels.append(doc["_id"])

        # 서버 채널 검색
        server_cursor = self.db["server-channels"].find(
            {"scrappers": scrapper_type.get_collection_name()}
        )
        for doc in server_cursor:
            channels.append(doc["_id"])

        return channels

    def add_scrapper(
        self,
        channel_id: str,
        channel_name: str,
        channel_type: str,
        scrapper_type: ScrapperType,
        guild_name: str = None,
    ) -> bool:
        """채널에 스크래퍼를 등록합니다."""
        if channel_type == "direct-messages":
            self.collection = self.db["direct-messages"]
        else:
            self.collection = self.db["server-channels"]

        update_data = {
            "user_name": channel_name,
            "channel_type": channel_type,
        }

        # 서버 채널인 경우에만 guild_name 추가
        if guild_name is not None:
            update_data = {
                "channel_name": channel_name,
                "channel_type": channel_type,
                "guild_name": guild_name,
            }

        result = self.collection.update_one(
            {"_id": channel_id},
            {
                "$set": update_data,
                "$addToSet": {"scrappers": scrapper_type.get_collection_name()},
            },
            upsert=True,
        )
        return result.modified_count > 0 or result.upserted_id is not None

    def remove_scrapper(
        self, channel_id: str, channel_type: str, scrapper_type: ScrapperType
    ) -> bool:
        """채널에서 스크래퍼를 제거합니다."""
        if channel_type == "direct-messages":
            collection = self.dm_collection
        else:
            collection = self.server_channel_collection
        result = collection.update_one(
            {"_id": channel_id},
            {"$pull": {"scrappers": scrapper_type.get_collection_name()}},
        )
        return result.modified_count > 0

    def get_channel_scrappers(self, channel_id: str) -> List[str]:
        """채널에 등록된 스크래퍼 목록을 반환합니다."""
        channel = self.dm_collection.find_one({"_id": channel_id})
        if channel:
            return channel.get("scrappers", [])
        channel = self.server_channel_collection.find_one({"_id": channel_id})
        return channel.get("scrappers", []) if channel else []
