@echo off
chcp 65001 >nul
echo ============================================================
echo 주식 매수 신호 모니터링 서버 시작 (백그라운드)
echo ============================================================
echo.

REM ============================================================
REM 텔레그램 봇 설정 (필수!)
REM ============================================================
set TELEGRAM_BOT_TOKEN=8015894529:AAEINiwSRY58nwtEMFZWOCmjK1nmbu_pEBU
set TELEGRAM_CHAT_ID=8130414883

REM ============================================================
REM 모니터링 설정 (선택사항)
REM ============================================================
set MONITOR_INTERVAL=60
set MONITOR_SYMBOL_COUNT=100
set MONITOR_WORKERS=20
set MONITOR_TIMEFRAME=short_swing
set PORT=5000
set HOST=0.0.0.0

echo 환경 변수 설정 완료
echo.
echo 서버를 백그라운드에서 시작합니다...
echo 터미널을 닫아도 서버는 계속 실행됩니다.
echo.

REM 새 PowerShell 창에서 서버 실행 (백그라운드)
start "주식 신호 모니터링 서버" powershell -NoExit -Command "cd '%~dp0'; $env:TELEGRAM_BOT_TOKEN='%TELEGRAM_BOT_TOKEN%'; $env:TELEGRAM_CHAT_ID='%TELEGRAM_CHAT_ID%'; $env:MONITOR_INTERVAL='%MONITOR_INTERVAL%'; $env:MONITOR_SYMBOL_COUNT='%MONITOR_SYMBOL_COUNT%'; $env:MONITOR_WORKERS='%MONITOR_WORKERS%'; $env:MONITOR_TIMEFRAME='%MONITOR_TIMEFRAME%'; $env:PORT='%PORT%'; $env:HOST='%HOST%'; python server.py"

echo.
echo 서버가 새 창에서 시작되었습니다.
echo 서버를 중지하려면 새 창을 닫으세요.
echo.
pause

