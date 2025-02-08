from enum import Enum
from typing import Dict, List, Optional
import json
import os

class CrawlerType(Enum):
    ACADEMIC = "academic"     # 학사공지
    SWACADEMIC = "swAcademic"  # SW학사공지
    SW = "sw"                # SW중심대학 공지
    # 추후 다른 크롤러 추가 가능

class CrawlerConfig:
    def __init__(self):
        self.CRAWLER_CONFIG_FILE = 'crawler_config.json'
        # channel_id -> List[CrawlerType]
        self.channel_crawlers: Dict[str, List[str]] = {}
        self.load_config()

    def load_config(self):
        """저장된 크롤러 설정을 불러옵니다."""
        try:
            if os.path.exists(self.CRAWLER_CONFIG_FILE):
                with open(self.CRAWLER_CONFIG_FILE, 'r') as f:
                    self.channel_crawlers = json.load(f)
        except Exception as e:
            print(f"크롤러 설정 로드 중 오류 발생: {e}")

    def save_config(self):
        """크롤러 설정을 파일에 저장합니다."""
        try:
            with open(self.CRAWLER_CONFIG_FILE, 'w') as f:
                json.dump(self.channel_crawlers, f)
        except Exception as e:
            print(f"크롤러 설정 저장 중 오류 발생: {e}")

    def add_crawler(self, channel_id: str, crawler_type: CrawlerType):
        """채널에 크롤러를 추가합니다."""
        if channel_id not in self.channel_crawlers:
            self.channel_crawlers[channel_id] = []
        
        if crawler_type.value not in self.channel_crawlers[channel_id]:
            self.channel_crawlers[channel_id].append(crawler_type.value)
            self.save_config()
            return True
        return False

    def remove_crawler(self, channel_id: str, crawler_type: CrawlerType):
        """채널에서 크롤러를 제거합니다."""
        if channel_id in self.channel_crawlers:
            if crawler_type.value in self.channel_crawlers[channel_id]:
                self.channel_crawlers[channel_id].remove(crawler_type.value)
                self.save_config()
                return True
        return False

    def get_channel_crawlers(self, channel_id: str) -> List[str]:
        """채널에 등록된 크롤러 목록을 반환합니다."""
        return self.channel_crawlers.get(channel_id, [])

    def get_channels_for_crawler(self, crawler_type: CrawlerType) -> List[str]:
        """특정 크롤러가 등록된 모든 채널을 반환합니다."""
        return [
            channel_id for channel_id, crawlers in self.channel_crawlers.items()
            if crawler_type.value in crawlers
        ] 