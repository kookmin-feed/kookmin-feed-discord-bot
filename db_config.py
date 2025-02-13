from pymongo import MongoClient
import os
from dotenv import load_dotenv
from notice_entry import NoticeEntry
from notice_type_map import NOTICE_TYPE_MAP

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'notice_bot')

_client = None

def get_database():
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client[DB_NAME]

def get_collection(collection_name: str):
    """지정된 이름의 MongoDB 컬렉션을 반환합니다."""
    db = get_database()
    return db[collection_name]

async def save_notice(notice: NoticeEntry, crawler_type):
    """공지사항을 DB에 저장합니다."""
    try:
        collection = get_collection(NOTICE_TYPE_MAP[crawler_type])
        collection.insert_one({
            'title': notice.title,
            'link': notice.link,
            'published': notice.published.isoformat(),
            'notice_type': notice.notice_type
        })
    except Exception as e:
        print(f"DB 저장 중 오류 발생: {e}")

def close_database():
    global _client
    if _client is not None:
        _client.close()
        _client = None 