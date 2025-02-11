# 국민대학교 공지사항 알리미 봇

디스코드를 통해 국민대학교 소프트웨어학부의 공지사항을 실시간으로 전달하는 봇입니다.

## 기능

- 실시간 공지사항 알림
  - 학사공지 (학부 홈페이지)
  - SW학사공지 (RSS 피드)
  - SW중심대학 공지사항
- 디스코드 채널 또는 DM으로 알림 수신
- 공지사항 종류별 구독 관리
- 테스트 기능

## 설치 방법

1. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

2. `.env` 파일 설정
```env
DISCORD_TOKEN=your_discord_bot_token
SWACADEMIC_RSS_URL=https://cs.kookmin.ac.kr/news/notice/rss
SW_URL=https://software.kookmin.ac.kr/software/bulletin/notice.do
ACADEMIC_URL=https://cs.kookmin.ac.kr/news/kookmin/academic/
MONGODB_URI=your_mongodb_connection_string
DB_NAME=your_database_name
```

## 사용 방법

### 봇 실행
```bash
python main.py
```

### 디스코드 명령어
- `/공지등록`: 공지사항 알림 등록
- `/공지삭제`: 공지사항 알림 삭제
- `/등록된공지`: 현재 등록된 알림 목록 확인
- `/testnotice`: 테스트 공지사항 전송 (디버그용)
- `/test-list`: 등록된 채널/유저 목록 확인 (디버그용)

## 프로젝트 구조

```
.
├── main.py                  # 프로그램 진입점
├── db_config.py            # 데이터베이스 설정
├── notice_entry.py         # 공지사항 데이터 모델
├── rss_feed_checker.py     # RSS 피드 파서
├── discord_bot/
│   ├── discord_bot.py      # 디스코드 봇 코어
│   ├── crawler_manager.py  # 크롤러 관리
│   └── commands/
│       ├── register.py     # 공지 등록 명령어
│       └── test.py         # 테스트 명령어
└── webcrawl/
    ├── academic_notice_checker.py  # 학사공지 크롤러
    └── sw_notice_checker.py        # SW중심대학 크롤러
```

## 데이터베이스 구조

### MongoDB 컬렉션

#### channels
- `_id`: 채널/유저 ID (string)
- `crawlers`: 등록된 크롤러 목록 (array)

#### academic_notice_history
- 학사공지 크롤링 기록
  - `title`: 제목
  - `link`: 링크
  - `published`: 작성일
  - `notice_type`: 'academic'

#### sw_notice_history
- SW중심대학 공지사항 기록
  - `title`: 제목
  - `link`: 링크
  - `published`: 작성일
  - `notice_type`: 'sw'

## 개발 정보

### 크롤링 주기
- 모든 크롤러: 5분 간격

### 공지사항 타입
- `academic`: 학사공지
- `swAcademic`: SW학사공지
- `sw`: SW중심대학 공지

## 주의사항

- 디스코드 봇 토큰 보안 유지
- MongoDB 연결 정보 보안
- 크롤링 간격 조절 시 서버 부하 고려
- 봇 권한 확인 (메시지 전송, 임베드 등)

## 라이선스

MIT License

## 기여하기

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request
