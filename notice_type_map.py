from discord_bot.crawler_type import CrawlerType

# 크롤러 타입과 notice_type 매핑
NOTICE_TYPE_MAP = {
    CrawlerType.ACADEMIC: 'academic',
    CrawlerType.SWACADEMIC: 'swAcademic',
    CrawlerType.SW: 'sw'
}

# 공지사항 종류별 한글 이름
NOTICE_TYPE_NAMES = {
    'academic': '학사공지',
    'swAcademic': 'SW학사공지',
    'sw': 'SW중심대학공지',
    'unknown': '알 수 없음'
} 