@echo off
chcp 65001 >nul
echo ============================================================
echo 주식 매수 신호 모니터링 서버 시작 (텔레그램 알림)
echo ============================================================
echo.

REM ============================================================
REM 텔레그램 봇 설정 (필수!)
REM ============================================================
REM 1. @BotFather에서 봇 토큰 받기
REM 2. @userinfobot에서 채팅 ID 확인
REM 3. 아래 값들을 실제 값으로 수정하세요
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

echo.
echo 환경 변수 설정 완료
echo.
echo 텔레그램 봇 토큰: %TELEGRAM_BOT_TOKEN:~0,20%...
echo 채팅 ID: %TELEGRAM_CHAT_ID%
echo 모니터링 간격: %MONITOR_INTERVAL%분
echo 모니터링 종목 수: %MONITOR_SYMBOL_COUNT%개
echo.
echo 서버 시작 중...
echo.

python server.py

pause

