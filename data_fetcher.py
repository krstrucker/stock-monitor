"""주식 데이터 가져오기"""
import yfinance as yf
import pandas as pd
import time
import json
import warnings
import logging
import os
from datetime import datetime, timedelta

# yfinance 경고 및 로그 억제
warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.ERROR)
os.environ['YFINANCE_DISABLE_WARNINGS'] = '1'

class YFRateLimitError(Exception):
    """yfinance API 제한 오류"""
    pass

def fetch_stock_data(symbol, period='6mo', retry_count=1, delay=0.3, silent=True, timeout=8):
    """주식 데이터 가져오기 (재시도 로직 포함, 조용한 모드, 빠른 실패)"""
    import sys
    from io import StringIO
    import threading
    
    # period를 6개월로 단축하여 더 빠른 응답
    if period == '1y':
        period = '6mo'
    
    result_container = {'data': None, 'error': None, 'done': False}
    
    def fetch_in_thread():
        """별도 스레드에서 데이터 가져오기"""
        try:
            if silent:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = StringIO()
                sys.stderr = StringIO()
            
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, timeout=timeout, raise_errors=False)
                
                if silent:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                
                result_container['data'] = hist
            except Exception as e:
                if silent:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                result_container['error'] = e
            finally:
                result_container['done'] = True
        except Exception as e:
            result_container['error'] = e
            result_container['done'] = True
    
    # 스레드에서 실행
    thread = threading.Thread(target=fetch_in_thread, daemon=True)
    thread.start()
    thread.join(timeout=timeout + 2)  # 타임아웃 + 여유 시간
    
    if not result_container['done']:
        # 타임아웃 발생
        return None
    
    if result_container['error']:
        return None
    
    hist = result_container['data']
                
    if hist is None or hist.empty:
        return None
    
    # 최소 데이터 포인트 확인 (최소 20일 이상, 6개월이면 약 120일)
    if len(hist) < 20:
        return None
    
    # 유효한 가격 데이터 확인
    if hist['Close'].isna().all() or hist['Close'].eq(0).all():
        return None
    
    return hist

def get_current_price(symbol):
    """현재 가격 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('currentPrice') or info.get('regularMarketPrice')
    except:
        return None

