@echo off
chcp 65001 >nul
echo ============================================================
echo Heroku 배포 스크립트
echo ============================================================
echo.

echo [1/8] Git 초기화...
git init
if errorlevel 1 (
    echo ❌ Git이 설치되지 않았거나 PATH에 없습니다.
    echo PowerShell을 재시작하거나 시스템을 재시작해주세요.
    pause
    exit /b 1
)

echo.
echo [2/8] Heroku 로그인 확인...
heroku --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Heroku CLI가 설치되지 않았거나 PATH에 없습니다.
    echo PowerShell을 재시작하거나 시스템을 재시작해주세요.
    pause
    exit /b 1
)

echo.
echo [3/8] Heroku 로그인...
heroku login
if errorlevel 1 (
    echo ❌ Heroku 로그인 실패
    pause
    exit /b 1
)

echo.
echo [4/8] Heroku 앱 생성...
set /p APP_NAME="앱 이름을 입력하세요 (예: my-stock-monitor): "
heroku create %APP_NAME%
if errorlevel 1 (
    echo ❌ 앱 생성 실패. 다른 이름을 시도해주세요.
    pause
    exit /b 1
)

echo.
echo [5/8] 환경 변수 설정...
heroku config:set TELEGRAM_BOT_TOKEN=8015894529:AAEINiwSRY58nwtEMFZWOCmjK1nmbu_pEBU
heroku config:set TELEGRAM_CHAT_ID=8130414883
heroku config:set MONITOR_INTERVAL=60
heroku config:set MONITOR_SYMBOL_COUNT=100

echo.
echo [6/8] Git 커밋...
git add .
git commit -m "Initial commit"

echo.
echo [7/8] Heroku에 배포...
git push heroku main
if errorlevel 1 (
    echo ❌ 배포 실패. 로그를 확인해주세요.
    heroku logs --tail
    pause
    exit /b 1
)

echo.
echo [8/8] 배포 완료!
echo.
echo ✅ 서버가 Heroku에서 실행 중입니다!
echo.
echo 로그 확인: heroku logs --tail
echo 앱 열기: heroku open
echo.
pause

