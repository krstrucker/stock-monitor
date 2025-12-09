# 주식 매수 신호 모니터링 서버

미국 주식 시장의 매수 신호를 자동으로 모니터링하고 텔레그램으로 알림을 보내는 서버입니다.

## 주요 기능

- ✅ 7.5점 이상 매수 신호 자동 감지
- ✅ 하루 2번 자동 스캔 (22:30, 02:30 KST)
- ✅ 텔레그램 알림
- ✅ 웹 대시보드
- ✅ 과거 스캔 기록 조회
- ✅ 종목별 차트 및 상세 정보

## 배포 방법

### Railway 배포 (권장)

1. GitHub에 코드 푸시
2. https://railway.app 접속
3. "Deploy from GitHub repo" 선택
4. 환경 변수 설정
5. 완료!

자세한 내용은 `Railway_빠른_배포_가이드.md` 참고

## 환경 변수

```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
MONITOR_SYMBOL_COUNT=0  # 0이면 전체
MONITOR_WORKERS=20
MONITOR_TIMEFRAME=short_swing
PORT=5000
HOST=0.0.0.0
```

## 로컬 실행

```bash
pip install -r requirements.txt
python server.py
```

또는

```bash
start_server.bat
```

## API 엔드포인트

- `GET /` - 대시보드
- `GET /status` - 서버 상태
- `GET /signals` - 현재 신호 목록
- `GET /scans` - 과거 스캔 기록
- `GET /symbol/<symbol>` - 종목 상세 정보
- `GET /chart/<symbol>` - 차트 데이터
- `GET /top-performers` - 주간/월간 TOP 10
- `POST /scan` - 즉시 스캔 실행

