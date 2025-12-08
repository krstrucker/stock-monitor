# 서버 배포 및 카카오톡 알림 설정 가이드

## 서버 배포 방법

### 1. 로컬 서버 실행

```bash
# 환경 변수 설정
export MONITOR_INTERVAL=60
export MONITOR_SYMBOL_COUNT=100
export MONITOR_WORKERS=20

# 서버 실행
python server.py
```

### 2. 클라우드 서버 배포 (예: AWS, Google Cloud, Heroku)

#### Heroku 배포 (가장 간단)

```bash
# Heroku CLI 설치 후
heroku create your-app-name
heroku config:set MONITOR_INTERVAL=60
heroku config:set MONITOR_SYMBOL_COUNT=100
git push heroku main
```

#### Docker 배포

```dockerfile
# Dockerfile 예시
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]
```

### 3. Linux 서버 배포 (systemd 서비스)

```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/stock-monitor.service
```

서비스 파일 내용:
```ini
[Unit]
Description=Stock Signal Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/us-stock-auto
Environment="MONITOR_INTERVAL=60"
Environment="MONITOR_SYMBOL_COUNT=100"
ExecStart=/usr/bin/python3 /path/to/us-stock-auto/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl enable stock-monitor
sudo systemctl start stock-monitor
sudo systemctl status stock-monitor
```

## 카카오톡 알림 설정

### 방법 1: 카카오톡 비즈니스 API (공식, 유료)

1. **카카오 개발자 센터 접속**
   - https://developers.kakao.com
   - 카카오 계정으로 로그인

2. **애플리케이션 생성**
   - 내 애플리케이션 > 애플리케이션 추가하기
   - 앱 이름, 사업자명 입력

3. **REST API 키 발급**
   - 앱 설정 > 앱 키에서 REST API 키 확인

4. **Admin 키 발급**
   - 앱 설정 > 앱 키에서 Admin 키 확인

5. **알림톡 서비스 신청**
   - 카카오 비즈니스 계정 필요
   - 알림톡 템플릿 생성

6. **환경 변수 설정**
```bash
export KAKAO_REST_API_KEY=your_rest_api_key
export KAKAO_ADMIN_KEY=your_admin_key
export KAKAO_TEMPLATE_ID=your_template_id
```

### 방법 2: 텔레그램 봇 (더 간단, 무료)

카카오톡 설정이 복잡하다면 텔레그램 봇을 사용할 수 있습니다.

1. **텔레그램 봇 생성**
   - 텔레그램에서 @BotFather 검색
   - `/newbot` 명령으로 봇 생성
   - 봇 토큰 받기

2. **채팅 ID 확인**
   - 텔레그램에서 @userinfobot 검색
   - 채팅 ID 확인

3. **환경 변수 설정**
```bash
export TELEGRAM_BOT_TOKEN=your_bot_token
export TELEGRAM_CHAT_ID=your_chat_id
```

## 환경 변수 설정

### .env 파일 사용 (권장)

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

### 직접 환경 변수 설정

```bash
# Linux/Mac
export MONITOR_INTERVAL=60
export MONITOR_SYMBOL_COUNT=100
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id

# Windows PowerShell
$env:MONITOR_INTERVAL = "60"
$env:MONITOR_SYMBOL_COUNT = "100"
$env:TELEGRAM_BOT_TOKEN = "your_token"
$env:TELEGRAM_CHAT_ID = "your_chat_id"
```

## 서버 실행

### 개발 모드
```bash
python server.py
```

### 프로덕션 모드 (Gunicorn 사용)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## 웹 인터페이스

서버 실행 후 브라우저에서 접속:
- http://localhost:5000 - 메인 페이지
- http://localhost:5000/status - 서버 상태
- http://localhost:5000/signals - 현재 신호 목록
- http://localhost:5000/scan - 즉시 스캔 실행

## API 엔드포인트

### GET /status
서버 상태 확인
```json
{
  "status": "running",
  "scheduler_running": true,
  "interval_minutes": 60,
  "symbol_count": 100
}
```

### GET /signals
현재 신호 목록
```json
{
  "signals": [
    {
      "symbol": "AAPL",
      "level": "STRONG_BUY",
      "score": 8.5,
      "price": 150.25
    }
  ],
  "count": 1
}
```

### POST /scan
즉시 스캔 실행

## 문제 해결

### 카카오톡 알림이 안 오는 경우
1. API 키 확인
2. 카카오 비즈니스 계정 확인
3. 알림톡 템플릿 승인 상태 확인
4. 텔레그램 봇을 대안으로 사용

### 서버가 자동으로 재시작되지 않는 경우
- systemd 서비스 설정 확인
- 로그 확인: `journalctl -u stock-monitor -f`

