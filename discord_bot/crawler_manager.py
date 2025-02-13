import json
import os
from enum import Enum
from typing import Dict, List, Optional
from db_config import get_database
from discord_bot.crawler_type import CrawlerType

class CrawlerConfig:
    """크롤러 설정을 관리하는 클래스"""
    def __init__(self):
        self.db = get_database()
        self.collection = self.db['crawler_config']
        
    def add_crawler(self, channel_id: str, crawler_type: CrawlerType) -> bool:
        """채널에 크롤러를 추가합니다."""
        result = self.collection.update_one(
            {'_id': channel_id},
            {'$addToSet': {'crawlers': crawler_type.value}},
            upsert=True
        )
        # upsert가 발생했거나, 배열이 수정되었으면 True 반환
        return result.upserted_id is not None or result.modified_count > 0

    def remove_crawler(self, channel_id: str, crawler_type: CrawlerType) -> bool:
        """채널에서 크롤러를 제거합니다."""
        result = self.collection.update_one(
            {'_id': channel_id},
            {'$pull': {'crawlers': crawler_type.value}}
        )
        return result.modified_count > 0

    def get_channel_crawlers(self, channel_id: str) -> List[str]:
        """채널에 등록된 크롤러 목록을 반환합니다."""
        channel = self.collection.find_one({'_id': channel_id})
        return channel.get('crawlers', []) if channel else []

    def get_channels_for_crawler(self, crawler_type: CrawlerType) -> list:
        """특정 크롤러에 등록된 채널 목록을 반환합니다."""
        config = self.collection.find_one({'crawler_type': crawler_type.value})
        return config['channels'] if config else [] 