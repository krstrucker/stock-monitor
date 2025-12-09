"""주식 데이터 가져오기 - 직접 Yahoo Finance API 호출"""
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

def fetch_stock_data(symbol, period='6mo', retry_count=1, delay=0.3, silent=True, timeout=8):
    """주식 데이터 가져오기 - 직접 Yahoo Finance API 호출 (yfinance 우회)"""
    import threading
    
    # period를 6개월로 단축
    if period == '1y':
        period = '6mo'
    
    result_container = {'data': None, 'error': None, 'done': False}
    
    def fetch_direct_api():
        """Yahoo Finance API 직접 호출"""
        try:
            # Yahoo Finance의 차트 API 직접 호출
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            range_param = '6mo' if period == '6mo' else '1y'
            
            params = {
                'interval': '1d',
                'range': range_param,
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
            
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                if not silent and symbol in ['AAPL', 'MSFT', 'GOOGL']:  # 테스트 종목만 로그
                    print(f"⚠️ {symbol}: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart'] or len(data['chart']['result']) == 0:
                if not silent and symbol in ['AAPL', 'MSFT', 'GOOGL']:
                    print(f"⚠️ {symbol}: chart.result 없음")
                return None
            
            result = data['chart']['result'][0]
            
            if 'timestamp' not in result or 'indicators' not in result:
                if not silent and symbol in ['AAPL', 'MSFT', 'GOOGL']:
                    print(f"⚠️ {symbol}: timestamp/indicators 없음")
                return None
            
            timestamps = result.get('timestamp', [])
            if not timestamps:
                return None
            
            indicators = result.get('indicators', {})
            quote_list = indicators.get('quote', [])
            if not quote_list:
                return None
            
            quote = quote_list[0]
            
            # 데이터 추출 및 None 값 처리
            opens = quote.get('open', [])
            highs = quote.get('high', [])
            lows = quote.get('low', [])
            closes = quote.get('close', [])
            volumes = quote.get('volume', [])
            
            # 유효한 데이터만 필터링 (None이 아닌 값만)
            valid_data = []
            valid_timestamps = []
            
            for i, ts in enumerate(timestamps):
                if i < len(closes) and closes[i] is not None and closes[i] > 0:
                    valid_timestamps.append(ts)
                    valid_data.append({
                        'Open': opens[i] if i < len(opens) and opens[i] is not None else closes[i],
                        'High': highs[i] if i < len(highs) and highs[i] is not None else closes[i],
                        'Low': lows[i] if i < len(lows) and lows[i] is not None else closes[i],
                        'Close': closes[i],
                        'Volume': volumes[i] if i < len(volumes) and volumes[i] is not None else 0
                    })
            
            if len(valid_data) < 20:
                if not silent and symbol in ['AAPL', 'MSFT', 'GOOGL']:
                    print(f"⚠️ {symbol}: 유효한 데이터 부족 ({len(valid_data)}개)")
                return None
            
            # DataFrame 생성
            try:
                df = pd.DataFrame(valid_data, index=pd.to_datetime(valid_timestamps, unit='s'))
            except Exception as e:
                if not silent and symbol in ['AAPL', 'MSFT', 'GOOGL']:
                    print(f"⚠️ {symbol}: DataFrame 생성 실패 - {str(e)}")
                return None
            
            # 최종 검증
            if df.empty or len(df) < 20:
                if not silent and symbol in ['AAPL', 'MSFT', 'GOOGL']:
                    print(f"⚠️ {symbol}: 최종 데이터 부족 ({len(df)}개)")
                return None
            
            return df
            
        except Exception as e:
            if not silent and symbol in ['AAPL', 'MSFT', 'GOOGL']:
                print(f"❌ {symbol}: API 호출 오류 - {str(e)}")
            return None
    
    def fetch_in_thread():
        """별도 스레드에서 데이터 가져오기"""
        try:
            # 방법 1: 직접 Yahoo Finance API 호출 (우선)
            hist = fetch_direct_api()
            if hist is not None and not hist.empty and len(hist) >= 20:
                result_container['data'] = hist
                result_container['done'] = True
                return
            
            # 방법 2: yfinance fallback (매우 짧은 타임아웃)
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, timeout=3, raise_errors=False)
                if hist is not None and not hist.empty and len(hist) >= 20:
                    result_container['data'] = hist
                    result_container['done'] = True
                    return
            except Exception as e:
                pass
            
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
    """현재 가격 가져오기 - 직접 API 호출"""
    try:
        # 직접 Yahoo Finance API 호출
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {'interval': '1d', 'range': '1d'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                if 'meta' in result:
                    return result['meta'].get('regularMarketPrice') or result['meta'].get('previousClose')
    except:
        pass
    
    # Fallback: yfinance
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('currentPrice') or info.get('regularMarketPrice')
    except:
        return None

