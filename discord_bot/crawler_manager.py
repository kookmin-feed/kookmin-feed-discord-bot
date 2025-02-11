from enum import Enum
from typing import Dict, List, Optional
from db_config import get_database

class CrawlerType(Enum):
    ACADEMIC = "academic"     # 학사공지
    SWACADEMIC = "swAcademic"  # SW학사공지
    SW = "sw"                # SW중심대학 공지
    # 추후 다른 크롤러 추가 가능

class CrawlerConfig:
    def __init__(self):
        self.db = get_database()
        self.channels_collection = self.db['channels']
        
    def add_crawler(self, channel_id: str, crawler_type: CrawlerType) -> bool:
        """채널에 크롤러를 추가합니다."""
        result = self.channels_collection.update_one(
            {'_id': channel_id},
            {'$addToSet': {'crawlers': crawler_type.value}},
            upsert=True
        )
        # upsert가 발생했거나, 배열이 수정되었으면 True 반환
        return result.upserted_id is not None or result.modified_count > 0

    def remove_crawler(self, channel_id: str, crawler_type: CrawlerType) -> bool:
        """채널에서 크롤러를 제거합니다."""
        result = self.channels_collection.update_one(
            {'_id': channel_id},
            {'$pull': {'crawlers': crawler_type.value}}
        )
        return result.modified_count > 0

    def get_channel_crawlers(self, channel_id: str) -> List[str]:
        """채널에 등록된 크롤러 목록을 반환합니다."""
        channel = self.channels_collection.find_one({'_id': channel_id})
        return channel.get('crawlers', []) if channel else []

    def get_channels_for_crawler(self, crawler_type: CrawlerType) -> List[str]:
        """특정 크롤러가 등록된 모든 채널을 반환합니다."""
        channels = self.channels_collection.find(
            {'crawlers': crawler_type.value},
            {'_id': 1}
        )
        return [str(channel['_id']) for channel in channels] 