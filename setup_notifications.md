# 알림 설정 가이드

## 텔레그램 봇 설정 (추천 - 가장 간단)

### 1. 텔레그램 봇 생성

1. 텔레그램 앱에서 **@BotFather** 검색
2. `/newbot` 명령 전송
3. 봇 이름 입력 (예: "주식 신호 봇")
4. 봇 사용자명 입력 (예: "my_stock_bot")
5. **봇 토큰 받기** (예: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. 채팅 ID 확인

1. 텔레그램에서 **@userinfobot** 검색
2. `/start` 명령 전송
3. **채팅 ID 확인** (예: `123456789`)

### 3. 환경 변수 설정

```bash
# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN = "your_bot_token"
$env:TELEGRAM_CHAT_ID = "your_chat_id"

# Linux/Mac
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### 4. 테스트

```python
from kakao_notifier import TelegramNotifier

notifier = TelegramNotifier()
notifier.send_message("테스트 메시지입니다!")
```

## 카카오톡 알림 설정 (고급)

### 1. 카카오 개발자 센터 접속
- https://developers.kakao.com
- 카카오 계정으로 로그인

### 2. 애플리케이션 생성
1. 내 애플리케이션 > 애플리케이션 추가하기
2. 앱 이름, 사업자명 입력

### 3. API 키 발급
1. 앱 설정 > 앱 키에서 **REST API 키** 확인
2. 앱 설정 > 앱 키에서 **Admin 키** 확인

### 4. 카카오 비즈니스 계정 필요
- 알림톡 사용을 위해서는 카카오 비즈니스 계정이 필요합니다
- https://business.kakao.com 에서 신청

### 5. 환경 변수 설정

```bash
export KAKAO_REST_API_KEY="your_rest_api_key"
export KAKAO_ADMIN_KEY="your_admin_key"
export KAKAO_TEMPLATE_ID="your_template_id"
```

## 빠른 시작 (텔레그램)

가장 빠르게 시작하려면 텔레그램 봇을 사용하세요:

```bash
# 1. 텔레그램 봇 토큰과 채팅 ID 설정
export TELEGRAM_BOT_TOKEN="123456789:ABC..."
export TELEGRAM_CHAT_ID="123456789"

# 2. 서버 실행
python server.py
```

이제 새로운 매수 신호가 나타나면 텔레그램으로 자동 알림이 옵니다!

