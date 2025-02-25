from typing import List
from config.db_config import get_database
from config.logger_config import setup_logger
from utils.scrapper_type import ScrapperType

logger = setup_logger(__name__)


class ScrapperConfig:
    """스크래퍼 설정을 관리하는 클래스"""

    def __init__(self):
        self.db = get_database()
        self.collection = self.db["scrapper_config"]

    def get_channels_for_scrapper(self, scrapper_type: ScrapperType) -> list:
        """특정 스크래퍼에 등록된 채널 목록을 반환합니다."""
        # 모든 문서를 검색하여 해당 스크래퍼가 등록된 채널 ID를 찾음
        channels = []
        cursor = self.collection.find(
            {"scrappers": scrapper_type.get_collection_name()}
        )
        for doc in cursor:
            channels.append(doc["_id"])
        return channels

    def add_scrapper(self, channel_id: str, scrapper_type: ScrapperType) -> bool:
        """채널에 스크래퍼를 추가합니다."""
        result = self.collection.update_one(
            {"_id": channel_id},
            {"$addToSet": {"scrappers": scrapper_type.get_collection_name()}},
            upsert=True,
        )
        return result.modified_count > 0 or result.upserted_id is not None

    def remove_scrapper(self, channel_id: str, scrapper_type: ScrapperType) -> bool:
        """채널에서 스크래퍼를 제거합니다."""
        result = self.collection.update_one(
            {"_id": channel_id},
            {"$pull": {"scrappers": scrapper_type.get_collection_name()}},
        )
        return result.modified_count > 0

    def get_channel_scrappers(self, channel_id: str) -> List[str]:
        """채널에 등록된 스크래퍼 목록을 반환합니다."""
        channel = self.collection.find_one({"_id": channel_id})
        return channel.get("scrappers", []) if channel else []
