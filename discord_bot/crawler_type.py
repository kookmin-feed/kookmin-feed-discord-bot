from enum import Enum

class CrawlerType(Enum):
    """크롤러 종류를 정의하는 열거형 클래스"""
    ACADEMIC = 'academic'      # 학사공지
    SWACADEMIC = 'swAcademic' # SW학사공지
    SW = 'sw'                 # SW중심대학 