#!/bin/bash

echo "============================================================"
echo "주식 매수 신호 모니터링 서버 시작 (텔레그램 알림)"
echo "============================================================"
echo ""

# ============================================================
# 텔레그램 봇 설정 (필수!)
# ============================================================
# 1. @BotFather에서 봇 토큰 받기
# 2. @userinfobot에서 채팅 ID 확인
# 3. 아래 값들을 실제 값으로 수정하세요
# ============================================================

export TELEGRAM_BOT_TOKEN="여기에_봇_토큰_입력"
export TELEGRAM_CHAT_ID="여기에_채팅_ID_입력"

# ============================================================
# 모니터링 설정 (선택사항)
# ============================================================
export MONITOR_INTERVAL=60
export MONITOR_SYMBOL_COUNT=100
export MONITOR_WORKERS=20
export MONITOR_TIMEFRAME=short_swing
export PORT=5000
export HOST=0.0.0.0

echo ""
echo "환경 변수 설정 완료"
echo ""
echo "텔레그램 봇 토큰: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "채팅 ID: $TELEGRAM_CHAT_ID"
echo "모니터링 간격: $MONITOR_INTERVAL분"
echo "모니터링 종목 수: $MONITOR_SYMBOL_COUNT개"
echo ""
echo "서버 시작 중..."
echo ""

python3 server.py

