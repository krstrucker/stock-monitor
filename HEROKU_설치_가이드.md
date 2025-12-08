# Heroku 배포 가이드

## 필요한 도구 설치

### 1단계: Git 설치
1. https://git-scm.com/download/win 접속
2. Windows용 Git 다운로드 및 설치
3. 설치 중 "Git from the command line and also from 3rd-party software" 선택

### 2단계: Heroku CLI 설치
1. https://devcenter.heroku.com/articles/heroku-cli 접속
2. Windows용 설치 프로그램 다운로드
3. 설치 완료 후 PowerShell 재시작

### 3단계: Heroku 계정 생성
1. https://www.heroku.com 접속
2. 무료 계정 생성

## 배포 단계

### 1. Heroku 로그인
```powershell
heroku login
```

### 2. 앱 생성
```powershell
heroku create your-stock-monitor
```

### 3. 환경 변수 설정
```powershell
heroku config:set TELEGRAM_BOT_TOKEN=8015894529:AAEINiwSRY58nwtEMFZWOCmjK1nmbu_pEBU
heroku config:set TELEGRAM_CHAT_ID=8130414883
heroku config:set MONITOR_INTERVAL=60
heroku config:set MONITOR_SYMBOL_COUNT=100
```

### 4. 배포
```powershell
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### 5. 로그 확인
```powershell
heroku logs --tail
```

## 주의사항
- Heroku 무료 티어는 제한이 있습니다
- 30분 동안 활동이 없으면 슬립 모드로 전환됩니다
- 월 550시간 무료 (약 23일)

