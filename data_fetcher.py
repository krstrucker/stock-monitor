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

def fetch_stock_data(symbol, period='1y', retry_count=2, delay=0.5, silent=True):
    """주식 데이터 가져오기 (재시도 로직 포함, 조용한 모드)"""
    import sys
    from io import StringIO
    
    for attempt in range(retry_count):
        try:
            # 표준 출력/에러 리다이렉트 (yfinance 메시지 억제)
            if silent:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = StringIO()
                sys.stderr = StringIO()
            
            try:
                ticker = yf.Ticker(symbol)
                
                # API 호출 간 딜레이 (rate limit 방지)
                if attempt > 0:
                    time.sleep(delay * (2 ** attempt))
                
                hist = ticker.history(period=period, timeout=10, raise_errors=False)
                
                # 출력 복원
                if silent:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                
                if hist is None or hist.empty:
                    return None
                
                # 최소 데이터 포인트 확인 (최소 20일 이상)
                if len(hist) < 20:
                    return None
                
                # 유효한 가격 데이터 확인
                if hist['Close'].isna().all() or hist['Close'].eq(0).all():
                    return None
                
                return hist
                
            except Exception as inner_e:
                # 출력 복원
                if silent:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                raise inner_e
                
        except json.JSONDecodeError:
            # JSON 파싱 오류 (API가 빈 응답 반환)
            if attempt < retry_count - 1:
                time.sleep(delay * (2 ** attempt))
            continue
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Rate limit 오류
            if 'rate' in error_str or 'too many' in error_str or '429' in error_str:
                wait_time = delay * (2 ** attempt) * 5  # 더 긴 대기
                if not silent:
                    print(f"⚠️ API 제한: {symbol}, {wait_time}초 대기...")
                time.sleep(wait_time)
                if attempt == retry_count - 1:
                    raise YFRateLimitError(f'Rate limited: {symbol}')
                continue
            
            # 상장폐지 또는 데이터 없음
            if ('delisted' in error_str or 'no data' in error_str or 
                'not found' in error_str or 'invalid' in error_str):
                return None
            
            # 네트워크 오류 등 - 재시도
            if attempt < retry_count - 1:
                time.sleep(delay * (2 ** attempt))
                continue
            
            # 마지막 시도 실패
            return None
    
    return None

def get_current_price(symbol):
    """현재 가격 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('currentPrice') or info.get('regularMarketPrice')
    except:
        return None

