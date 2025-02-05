class NoticeEntry:
    """공지사항 항목을 표현하는 클래스입니다."""
    
    def __init__(self, entry):
        """
        공지사항 항목을 초기화합니다.
        
        Args:
            entry (dict): 공지사항 정보를 담은 딕셔너리
        """
        self.title = entry['title']
        self.published = entry['published']
        self.link = entry['link']
        self.separator = '-' * 80
    
    def __str__(self):
        """공지사항 항목을 문자열로 표현합니다."""
        return (
            f"\n제목: {self.title}\n"
            f"작성일: {self.published.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"링크: {self.link}\n"
            f"{self.separator}"
        )

    def __eq__(self, other):
        """두 공지사항이 같은지 비교합니다."""
        if not isinstance(other, NoticeEntry):
            return False
        # articleNo를 기준으로 비교
        return self.get_article_no() == other.get_article_no()

    def __hash__(self):
        """공지사항의 해시값을 반환합니다."""
        # articleNo를 기준으로 해시
        return hash(self.get_article_no())

    def get_article_no(self):
        """공지사항의 고유 번호를 추출합니다."""
        try:
            return self.link.split('articleNo=')[1].split('&')[0]
        except:
            return self.link  # 실패시 전체 링크를 반환 