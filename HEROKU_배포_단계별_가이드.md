# Heroku 배포 단계별 가이드

## ⚠️ 중요: PowerShell 재시작 필요

Git과 Heroku CLI를 설치한 후에는 **PowerShell을 완전히 종료하고 다시 열어야** 합니다.

## 1단계: PowerShell 재시작

1. 현재 PowerShell 창을 **완전히 닫기**
2. 새 PowerShell 창 열기
3. 프로젝트 폴더로 이동:
   ```powershell
   cd "C:\Users\용\Desktop\us stock auto"
   ```

## 2단계: 설치 확인

```powershell
git --version
heroku --version
```

둘 다 버전이 표시되면 정상입니다!

## 3단계: Heroku 로그인

```powershell
heroku login
```

브라우저가 열리면 로그인하세요.

## 4단계: Heroku 앱 생성

```powershell
heroku create your-stock-monitor
```

앱 이름이 이미 사용 중이면 다른 이름을 사용하세요.

## 5단계: 환경 변수 설정

```powershell
heroku config:set TELEGRAM_BOT_TOKEN=8015894529:AAEINiwSRY58nwtEMFZWOCmjK1nmbu_pEBU
heroku config:set TELEGRAM_CHAT_ID=8130414883
heroku config:set MONITOR_INTERVAL=60
heroku config:set MONITOR_SYMBOL_COUNT=100
```

## 6단계: Git 초기화 및 커밋

```powershell
git init
git add .
git commit -m "Initial commit"
```

## 7단계: Heroku에 배포

```powershell
git push heroku main
```

## 8단계: 로그 확인

```powershell
heroku logs --tail
```

## 문제 해결

### Git/Heroku가 인식되지 않는 경우

1. **PowerShell 완전히 재시작**
2. **시스템 재시작** (필요한 경우)
3. **전체 경로로 실행**:
   ```powershell
   # Git 전체 경로 찾기
   where.exe git
   
   # Heroku 전체 경로 찾기
   where.exe heroku
   ```

### 배포 오류가 발생하는 경우

1. **Procfile 확인**: `web: python server.py` 형식인지 확인
2. **requirements.txt 확인**: 모든 패키지가 포함되어 있는지 확인
3. **로그 확인**: `heroku logs --tail`로 오류 메시지 확인

