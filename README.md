# 국민대학교 공지사항 알림 디스코드 봇

국민대학교 소프트웨어융합대학 및 SW중심대학 공지사항 업데이트를 디스코드 서버에 알려주는 봇입니다.

## 주요 기능

- 소프트웨어융합대학 공지사항 모니터링 및 알림
- SW중심대학 공지사항 모니터링 및 알림
- 디스코드 채널별 맞춤 알림 설정
- 자동 주기적 업데이트 확인

## 설치 방법

1. 저장소를 클론합니다:
```
git clone https://github.com/sinam7/kookmin-feed.git
```

2. 필요한 패키지를 설치합니다:
```
pip install -r requirements.txt
```

3. `.env` 파일을 생성하고 다음 환경 변수를 설정합니다:
```
DISCORD_TOKEN=your_discord_bot_token
```

4. `channel_config.json`에서 채널 설정을 구성합니다.

## 실행 방법

```
python main.py
```

## 파일 구조

- `main.py`: 메인 실행 파일
- `discord_bot.py`: 디스코드 봇 구현
- `notice_checker.py`: 공지사항 확인 로직
- `notice_entry.py`: 공지사항 데이터 모델
- `channel_config.json`: 채널 설정 파일
- `notice_history.json`: 공지사항 기록 저장

## 디스코드 명령어

### 채널 설정 명령어
```
/setchannel [channel] - 공지사항을 받을 채널을 설정합니다
  - channel: 설정할 채널 (미지정시 현재 채널)
  - 관리자 권한이 필요합니다

/getchannel - 현재 설정된 공지 채널을 확인합니다
```