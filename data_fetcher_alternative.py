"""주식 데이터 가져오기 - 대안 방법"""
import pandas as pd
import time
import json
import warnings
import logging
import os
import requests
from datetime import datetime, timedelta
import yfinance as yf

# 경고 억제
warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.CRITICAL)
os.environ['YFINANCE_DISABLE_WARNINGS'] = '1'

class YFRateLimitError(Exception):
    """yfinance API 제한 오류"""
    pass

def fetch_stock_data_direct(symbol, period='6mo'):
    """Yahoo Finance를 직접 스크래핑 (yfinance 우회)"""
    try:
        # Yahoo Finance의 차트 API 직접 호출
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            'interval': '1d',
            'range': '6mo' if period == '6mo' else '1y',
            'includePrePost': 'false',
            'events': 'div,splits'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://finance.yahoo.com/',
            'Origin': 'https://finance.yahoo.com'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if 'chart' not in data or 'result' not in data['chart']:
            return None
        
        result = data['chart']['result'][0]
        
        if 'timestamp' not in result or 'indicators' not in result:
            return None
        
        timestamps = result['timestamp']
        quote = result['indicators']['quote'][0]
        
        # DataFrame 생성
        df = pd.DataFrame({
            'Open': quote['open'],
            'High': quote['high'],
            'Low': quote['low'],
            'Close': quote['close'],
            'Volume': quote['volume']
        }, index=pd.to_datetime(timestamps, unit='s'))
        
        # NaN 제거
        df = df.dropna()
        
        if df.empty or len(df) < 20:
            return None
        
        return df
        
    except Exception as e:
        return None

def fetch_stock_data_yfinance_fallback(symbol, period='6mo', timeout=5):
    """yfinance를 사용하되 빠르게 실패"""
    try:
        ticker = yf.Ticker(symbol)
        # 매우 짧은 타임아웃으로 빠르게 실패
        hist = ticker.history(period=period, timeout=timeout, raise_errors=False)
        
        if hist is None or hist.empty or len(hist) < 20:
            return None
        
        return hist
    except:
        return None

def fetch_stock_data(symbol, period='6mo', retry_count=1, delay=0.3, silent=True, timeout=8):
    """주식 데이터 가져오기 (여러 방법 시도)"""
    import threading
    
    # period를 6개월로 단축
    if period == '1y':
        period = '6mo'
    
    result_container = {'data': None, 'error': None, 'done': False}
    
    def fetch_in_thread():
        """별도 스레드에서 데이터 가져오기"""
        try:
            # 방법 1: 직접 Yahoo Finance API 호출 시도
            hist = fetch_stock_data_direct(symbol, period)
            if hist is not None and not hist.empty:
                result_container['data'] = hist
                result_container['done'] = True
                return
            
            # 방법 2: yfinance 사용 (fallback)
            hist = fetch_stock_data_yfinance_fallback(symbol, period, timeout=5)
            if hist is not None and not hist.empty:
                result_container['data'] = hist
                result_container['done'] = True
                return
            
            # 모두 실패
            result_container['done'] = True
            
        except Exception as e:
            result_container['error'] = e
            result_container['done'] = True
    
    # 스레드에서 실행
    thread = threading.Thread(target=fetch_in_thread, daemon=True)
    thread.start()
    thread.join(timeout=timeout + 2)
    
    if not result_container['done']:
        return None
    
    if result_container['error']:
        return None
    
    hist = result_container['data']
    
    if hist is None or hist.empty:
        return None
    
    # 최소 데이터 포인트 확인
    if len(hist) < 20:
        return None
    
    # 유효한 가격 데이터 확인
    if hist['Close'].isna().all() or hist['Close'].eq(0).all():
        return None
    
    return hist

def get_current_price(symbol):
    """현재 가격 가져오기"""
    try:
        # 직접 API 호출 시도
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {'interval': '1d', 'range': '1d'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                if 'meta' in result:
                    return result['meta'].get('regularMarketPrice')
    except:
        pass
    
    # Fallback: yfinance
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('currentPrice') or info.get('regularMarketPrice')
    except:
        return None

