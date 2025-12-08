# 카카오톡 알림 설정 가이드

## 카카오톡 알림 설정 방법

카카오톡으로 알림을 받으려면 **카카오 비즈니스 계정**이 필요합니다. 
더 간단한 방법으로는 **텔레그램 봇**을 사용할 수 있습니다.

## 방법 1: 카카오톡 알림톡 API (공식, 유료)

### 단계별 설정

#### 1단계: 카카오 개발자 센터 접속
- https://developers.kakao.com 접속
- 카카오 계정으로 로그인

#### 2단계: 애플리케이션 생성
1. **내 애플리케이션** 클릭
2. **애플리케이션 추가하기** 클릭
3. 앱 이름 입력 (예: "주식 신호 알림")
4. 사업자명 입력
5. **저장** 클릭

#### 3단계: REST API 키 확인
1. 생성한 애플리케이션 클릭
2. **앱 설정** > **앱 키** 메뉴
3. **REST API 키** 복사

#### 4단계: Admin 키 확인
1. **앱 설정** > **앱 키** 메뉴
2. **Admin 키** 복사 (보안을 위해 중요!)

#### 5단계: 카카오 비즈니스 계정 신청
- https://business.kakao.com 접속
- 카카오 비즈니스 계정 신청 (유료 서비스)
- 알림톡 서비스 활성화

#### 6단계: 알림톡 템플릿 생성
1. 카카오 비즈니스 콘솔 접속
2. **알림톡** > **템플릿 관리**
3. 새 템플릿 생성
4. 템플릿 내용 작성 (예: "주식 매수 신호 알림")
5. 템플릿 승인 대기
6. **템플릿 ID** 복사

#### 7단계: 환경 변수 설정

**Windows PowerShell:**
```powershell
$env:KAKAO_REST_API_KEY = "여기에_REST_API_키_붙여넣기"
$env:KAKAO_ADMIN_KEY = "여기에_Admin_키_붙여넣기"
$env:KAKAO_TEMPLATE_ID = "여기에_템플릿_ID_붙여넣기"
$env:MONITOR_INTERVAL = "60"
$env:MONITOR_SYMBOL_COUNT = "100"
```

**Linux/Mac:**
```bash
export KAKAO_REST_API_KEY="여기에_REST_API_키_붙여넣기"
export KAKAO_ADMIN_KEY="여기에_Admin_키_붙여넣기"
export KAKAO_TEMPLATE_ID="여기에_템플릿_ID_붙여넣기"
export MONITOR_INTERVAL=60
export MONITOR_SYMBOL_COUNT=100
```

#### 8단계: 서버 실행
```bash
python server.py
```

## 방법 2: 텔레그램 봇 (더 간단, 무료, 추천!)

카카오톡 설정이 복잡하다면 텔레그램 봇을 사용하는 것을 강력히 추천합니다.

### 단계별 설정 (5분이면 완료!)

#### 1단계: 텔레그램 봇 생성
1. 텔레그램 앱 열기
2. 검색창에 **@BotFather** 입력
3. 봇과 대화 시작
4. `/newbot` 명령 전송
5. 봇 이름 입력 (예: "내 주식 신호 봇")
6. 봇 사용자명 입력 (예: "my_stock_signal_bot")
7. **봇 토큰 받기** (예: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
8. **봇 토큰 복사해두기**

#### 2단계: 채팅 ID 확인
1. 텔레그램에서 **@userinfobot** 검색
2. 봇과 대화 시작
3. `/start` 명령 전송
4. **채팅 ID 확인** (예: `123456789`)
5. **채팅 ID 복사해두기**

#### 3단계: 환경 변수 설정

**Windows PowerShell:**
```powershell
$env:TELEGRAM_BOT_TOKEN = "여기에_봇_토큰_붙여넣기"
$env:TELEGRAM_CHAT_ID = "여기에_채팅_ID_붙여넣기"
$env:MONITOR_INTERVAL = "60"
$env:MONITOR_SYMBOL_COUNT = "100"
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="여기에_봇_토큰_붙여넣기"
export TELEGRAM_CHAT_ID="여기에_채팅_ID_붙여넣기"
export MONITOR_INTERVAL=60
export MONITOR_SYMBOL_COUNT=100
```

#### 4단계: 서버 실행
```bash
python server.py
```

## 서버 배포 방법

### 로컬 서버 (Windows)

#### 방법 1: PowerShell에서 직접 실행
```powershell
# 환경 변수 설정
$env:TELEGRAM_BOT_TOKEN = "your_token"
$env:TELEGRAM_CHAT_ID = "your_chat_id"
$env:MONITOR_INTERVAL = "60"
$env:MONITOR_SYMBOL_COUNT = "100"

# 서버 실행
python server.py
```

#### 방법 2: 배치 파일로 실행
`start_server.bat` 파일 생성:
```batch
@echo off
set TELEGRAM_BOT_TOKEN=your_token
set TELEGRAM_CHAT_ID=your_chat_id
set MONITOR_INTERVAL=60
set MONITOR_SYMBOL_COUNT=100
python server.py
pause
```

### 클라우드 서버 (Heroku - 무료)

#### 1단계: Heroku 계정 생성
- https://www.heroku.com 접속
- 무료 계정 생성

#### 2단계: Heroku CLI 설치
- https://devcenter.heroku.com/articles/heroku-cli
- Windows용 다운로드 및 설치

#### 3단계: 프로젝트 배포
```bash
# Heroku 로그인
heroku login

# Heroku 앱 생성
heroku create your-app-name

# 환경 변수 설정
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set TELEGRAM_CHAT_ID=your_chat_id
heroku config:set MONITOR_INTERVAL=60
heroku config:set MONITOR_SYMBOL_COUNT=100

# 배포
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

#### 4단계: 로그 확인
```bash
heroku logs --tail
```

### Linux 서버 (VPS, AWS 등)

#### 1단계: 서버 접속
```bash
ssh user@your-server-ip
```

#### 2단계: 프로젝트 업로드
```bash
# Git 사용
git clone your-repo-url
cd us-stock-auto

# 또는 SCP로 파일 전송
scp -r . user@server:/path/to/us-stock-auto
```

#### 3단계: 환경 변수 설정
```bash
# .env 파일 생성
nano .env
```

`.env` 파일 내용:
```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
MONITOR_INTERVAL=60
MONITOR_SYMBOL_COUNT=100
```

#### 4단계: systemd 서비스 생성
```bash
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
EnvironmentFile=/path/to/us-stock-auto/.env
ExecStart=/usr/bin/python3 /path/to/us-stock-auto/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 5단계: 서비스 시작
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-monitor
sudo systemctl start stock-monitor
sudo systemctl status stock-monitor
```

#### 6단계: 로그 확인
```bash
sudo journalctl -u stock-monitor -f
```

## 테스트 방법

### 1. 알림 테스트
```python
from kakao_notifier import TelegramNotifier

# 텔레그램 알림 테스트
notifier = TelegramNotifier()
notifier.send_message("테스트 메시지입니다! 🎉")
```

### 2. 서버 상태 확인
브라우저에서 접속:
- http://localhost:5000/status

### 3. 즉시 스캔 실행
브라우저에서 접속:
- http://localhost:5000/scan

## 문제 해결

### 알림이 안 오는 경우
1. **봇 토큰 확인**: @BotFather에서 `/token` 명령으로 확인
2. **채팅 ID 확인**: @userinfobot에서 다시 확인
3. **봇과 대화 시작**: 텔레그램에서 봇에게 `/start` 명령 전송
4. **환경 변수 확인**: `echo $TELEGRAM_BOT_TOKEN` (Linux) 또는 `echo $env:TELEGRAM_BOT_TOKEN` (PowerShell)

### 서버가 실행되지 않는 경우
1. **포트 확인**: 다른 프로그램이 5000번 포트를 사용 중인지 확인
2. **포트 변경**: `$env:PORT = "5001"` (PowerShell)
3. **로그 확인**: 서버 실행 시 출력되는 오류 메시지 확인

### 서버가 자동으로 재시작되지 않는 경우
1. **systemd 서비스 확인**: `sudo systemctl status stock-monitor`
2. **로그 확인**: `sudo journalctl -u stock-monitor -n 50`

## 추천 설정

### 개발/테스트
```powershell
$env:MONITOR_INTERVAL = "10"  # 10분마다 (빠른 테스트)
$env:MONITOR_SYMBOL_COUNT = "50"  # 50개 종목만
```

### 프로덕션
```powershell
$env:MONITOR_INTERVAL = "60"  # 1시간마다
$env:MONITOR_SYMBOL_COUNT = "200"  # 200개 종목
$env:MONITOR_WORKERS = "30"  # 더 많은 스레드
```

## 완료!

이제 서버가 백그라운드에서 자동으로:
- ✅ 주기적으로 스캔 실행
- ✅ 새로운 매수 신호 발견 시 카카오톡/텔레그램으로 알림
- ✅ 웹 인터페이스로 상태 확인 가능
- ✅ 24시간 자동 실행

