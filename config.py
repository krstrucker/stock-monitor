"""설정 파일"""
import os

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# 모니터링 설정
MONITOR_INTERVAL = int(os.environ.get('MONITOR_INTERVAL', '60'))  # 분
MONITOR_SYMBOL_COUNT = int(os.environ.get('MONITOR_SYMBOL_COUNT', '0'))  # 0이면 전체
MONITOR_WORKERS = int(os.environ.get('MONITOR_WORKERS', '20'))
MONITOR_TIMEFRAME = os.environ.get('MONITOR_TIMEFRAME', 'short_swing')

# 서버 설정
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '5000'))

# 기본 종목 리스트 (전체 스캔용)
# 실제로는 symbol_fetcher.py에서 동적으로 가져옴
DEFAULT_SYMBOLS = []

