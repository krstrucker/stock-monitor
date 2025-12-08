# 빠른 시작 가이드

## 서버 실행 및 알림 설정

### 1단계: 텔레그램 봇 설정 (5분)

#### 텔레그램 봇 생성
1. 텔레그램 앱 열기
2. 검색창에 **@BotFather** 입력
3. `/newbot` 명령 전송
4. 봇 이름 입력 (예: "내 주식 신호 봇")
5. 봇 사용자명 입력 (예: "my_stock_signal_bot")
6. **봇 토큰 복사** (예: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 채팅 ID 확인
1. 텔레그램에서 **@userinfobot** 검색
2. `/start` 명령 전송
3. **채팅 ID 복사** (예: `123456789`)

### 2단계: 환경 변수 설정

#### Windows PowerShell
```powershell
$env:TELEGRAM_BOT_TOKEN = "여기에_봇_토큰_붙여넣기"
$env:TELEGRAM_CHAT_ID = "여기에_채팅_ID_붙여넣기"
$env:MONITOR_INTERVAL = "60"
$env:MONITOR_SYMBOL_COUNT = "100"
```

#### Linux/Mac
```bash
export TELEGRAM_BOT_TOKEN="여기에_봇_토큰_붙여넣기"
export TELEGRAM_CHAT_ID="여기에_채팅_ID_붙여넣기"
export MONITOR_INTERVAL=60
export MONITOR_SYMBOL_COUNT=100
```

### 3단계: 패키지 설치
```bash
pip install -r requirements.txt
```

### 4단계: 서버 실행
```bash
python server.py
```

## 완료! 🎉

이제 서버가 백그라운드에서 자동으로:
- ✅ 60분마다 자동 스캔
- ✅ 새로운 매수 신호 발견 시 텔레그램으로 알림
- ✅ 웹 인터페이스 제공 (http://localhost:5000)

## 웹 인터페이스

브라우저에서 접속:
- **http://localhost:5000** - 메인 대시보드
- **http://localhost:5000/status** - 서버 상태 확인
- **http://localhost:5000/signals** - 현재 신호 목록 (JSON)
- **http://localhost:5000/scan** - 즉시 스캔 실행

## 서버 중지

Ctrl+C를 누르면 안전하게 중지됩니다.

## 24시간 실행 (서버 배포)

### 방법 1: systemd (Linux)
```bash
sudo systemctl enable stock-monitor
sudo systemctl start stock-monitor
```

### 방법 2: Heroku (클라우드)
```bash
heroku create your-app-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set TELEGRAM_CHAT_ID=your_chat_id
git push heroku main
```

### 방법 3: Docker
```bash
docker build -t stock-monitor .
docker run -d -p 5000:5000 \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  stock-monitor
```

## 알림 예시

새로운 매수 신호가 나타나면 텔레그램으로 다음과 같은 메시지가 옵니다:

```
🔔 새로운 매수 신호 발견! (3개)

🟢 AAPL: 강한 매수
   점수: 8.5/10
   가격: $150.25

🔵 MSFT: 매수
   점수: 6.2/10
   가격: $380.50

🟡 GOOGL: 관망 매수
   점수: 4.5/10
   가격: $140.20

⏰ 2025-12-05 14:30:00
```

