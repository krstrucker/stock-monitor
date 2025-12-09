"""주식 데이터 가져오기"""
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

class YFRateLimitError(Exception):
    """yfinance API 제한 오류"""
    pass

def fetch_stock_data(symbol, period='1y', retry_count=3, delay=1):
    """주식 데이터 가져오기 (재시도 로직 포함)"""
    for attempt in range(retry_count):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # API 제한 확인
            if 'Too Many Requests' in str(hist):
                raise YFRateLimitError('Too Many Requests. Rate limited. Try after a while.')
            
            return hist
        except Exception as e:
            error_str = str(e)
            if 'Rate limited' in error_str or 'Too Many Requests' in error_str:
                wait_time = delay * (2 ** attempt)  # 지수 백오프
                print(f"⚠️ API 제한: {symbol}, {wait_time}초 대기...")
                time.sleep(wait_time)
                if attempt == retry_count - 1:
                    raise YFRateLimitError(error_str)
            else:
                if attempt == retry_count - 1:
                    return None
                time.sleep(delay)
    
    return None

def get_current_price(symbol):
    """현재 가격 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('currentPrice') or info.get('regularMarketPrice')
    except:
        return None

