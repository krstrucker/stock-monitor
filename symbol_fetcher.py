"""종목 리스트 가져오기 - NYSE & NASDAQ"""
import yfinance as yf
import pandas as pd
import requests
import time
import os
import re

def filter_valid_symbols(symbols):
    """유효한 종목만 필터링 (상장폐지, 우선주 제외)"""
    valid = []
    
    for symbol in symbols:
        if not symbol or not isinstance(symbol, str):
            continue
        
        symbol = symbol.strip().upper()
        
        # 기본 필터링
        if len(symbol) == 0 or len(symbol) > 5:
            continue
        
        # 우선주 제외 패턴
        # - .PR (Preferred Stock)
        # - -A, -B, -C 등 (클래스별 주식, 일부는 우선주)
        # - 숫자로 끝나는 패턴 (예: ABC1, XYZ2 - 우선주 가능성)
        if ('.PR' in symbol or 
            symbol.endswith('-P') or 
            any(symbol.endswith(f'-{chr(i)}') for i in range(65, 91)) or  # -A ~ -Z
            re.match(r'^[A-Z]+[0-9]+$', symbol)):  # ABC1, XYZ2 같은 패턴
            continue
        
        # 특수 문자 제외
        if ('^' in symbol or '/' in symbol or '$' in symbol or 
            '.' in symbol or '-' in symbol or ' ' in symbol):
            continue
        
        # 상장폐지 의심 종목 제외 (너무 짧거나 특수 패턴)
        if len(symbol) < 1:
            continue
        
        valid.append(symbol)
    
    return valid

def get_nasdaq_symbols():
    """NASDAQ 종목 리스트 가져오기"""
    symbols = []
    try:
        # NASDAQ API
        nasdaq_url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&offset=0&download=true"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nasdaq.com/',
            'Origin': 'https://www.nasdaq.com'
        }
        
        response = requests.get(nasdaq_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'rows' in data['data']:
                for row in data['data']['rows']:
                    symbol = row.get('symbol', '').strip().upper()
                    if symbol:
                        symbols.append(symbol)
                print(f"✅ NASDAQ에서 {len(symbols)}개 종목 가져옴")
        else:
            print(f"⚠️ NASDAQ API 응답 코드: {response.status_code}")
    except Exception as e:
        print(f"⚠️ NASDAQ API 실패: {str(e)}")
    
    return symbols

def get_nyse_symbols():
    """NYSE 종목 리스트 가져오기"""
    symbols = []
    try:
        # NYSE API (NASDAQ API와 동일한 구조 사용)
        nyse_url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&exchange=NYSE&limit=10000&offset=0&download=true"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nasdaq.com/',
            'Origin': 'https://www.nasdaq.com'
        }
        
        response = requests.get(nyse_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'rows' in data['data']:
                for row in data['data']['rows']:
                    symbol = row.get('symbol', '').strip().upper()
                    if symbol:
                        symbols.append(symbol)
                print(f"✅ NYSE에서 {len(symbols)}개 종목 가져옴")
        else:
            print(f"⚠️ NYSE API 응답 코드: {response.status_code}")
    except Exception as e:
        print(f"⚠️ NYSE API 실패: {str(e)}")
    
    # 백업 방법: Wikipedia에서 S&P 500 종목 가져오기 (대부분 NYSE/NASDAQ)
    if len(symbols) < 100:
        try:
            print("📊 Wikipedia에서 S&P 500 종목 가져오는 중...")
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(sp500_url)
            if len(tables) > 0:
                sp500_table = tables[0]
                if 'Symbol' in sp500_table.columns:
                    wiki_symbols = sp500_table['Symbol'].tolist()
                    symbols.extend(wiki_symbols)
                    print(f"✅ Wikipedia에서 {len(wiki_symbols)}개 종목 추가")
        except Exception as e:
            print(f"⚠️ Wikipedia 가져오기 실패: {str(e)}")
    
    return symbols

def get_all_symbols():
    """모든 미국 주식 종목 리스트 가져오기 (NYSE + NASDAQ, 상장폐지/우선주 제외)"""
    try:
        all_symbols = []
        
        print("📊 NYSE & NASDAQ 종목 리스트 가져오는 중...")
        
        # NASDAQ 종목 가져오기
        nasdaq_symbols = get_nasdaq_symbols()
        all_symbols.extend(nasdaq_symbols)
        
        # 잠시 대기 (API 제한 방지)
        time.sleep(1)
        
        # NYSE 종목 가져오기
        nyse_symbols = get_nyse_symbols()
        all_symbols.extend(nyse_symbols)
        
        # 중복 제거
        all_symbols = list(set(all_symbols))
        print(f"📊 필터링 전: {len(all_symbols)}개 종목")
        
        # 유효한 종목만 필터링 (상장폐지, 우선주 제외)
        valid_symbols = filter_valid_symbols(all_symbols)
        
        # 정렬
        valid_symbols = sorted(valid_symbols)
        
        excluded_count = len(all_symbols) - len(valid_symbols)
        print(f"✅ 종목 리스트 로드 완료: 총 {len(valid_symbols)}개")
        print(f"   - 제외된 종목: {excluded_count}개 (우선주, 상장폐지, 특수문자 등)")
        
        # 최소한의 종목이 있어야 함
        if len(valid_symbols) < 50:
            print("⚠️ 종목 수가 적습니다. 백업 리스트 사용...")
            backup_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA',
                'V', 'UNH', 'JNJ', 'WMT', 'JPM', 'MA', 'PG', 'HD', 'DIS', 'BAC',
                'XOM', 'CVX', 'ABBV', 'PFE', 'AVGO', 'COST', 'MRK', 'PEP', 'TMO', 'CSCO',
                'ABT', 'ACN', 'DHR', 'VZ', 'ADBE', 'NFLX', 'CMCSA', 'NKE', 'TXN', 'NEE',
                'LIN', 'PM', 'QCOM', 'HON', 'UNP', 'LOW', 'RTX', 'UPS', 'INTU', 'SPGI',
                'SBUX', 'GS', 'CAT', 'DE', 'AXP', 'BLK', 'BKNG', 'ADP', 'TJX', 'GE',
                'MDT', 'ZTS', 'SYK', 'ISRG', 'CI', 'ELV', 'GILD', 'MO', 'AMGN', 'SHW',
                'LMT', 'ICE', 'PLD', 'APH', 'KLAC', 'CDNS', 'SNPS', 'FTNT', 'ANSS', 'MCHP',
                'SWKS', 'QRVO', 'CRWD', 'ZS', 'NET', 'DDOG', 'OKTA', 'DOCN', 'FROG', 'ESTC',
                'MDB', 'NOW', 'TEAM', 'ZM', 'DOCU', 'COUP', 'BILL', 'ASAN', 'WK', 'FRSH'
            ]
            valid_symbols.extend(backup_symbols)
            valid_symbols = sorted(list(set(valid_symbols)))
            valid_symbols = filter_valid_symbols(valid_symbols)
            print(f"✅ 백업 리스트 추가 후: {len(valid_symbols)}개")
        
        return valid_symbols
        
    except Exception as e:
        print(f"❌ 종목 리스트 가져오기 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        # 최소한의 종목 리스트라도 반환
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'V', 'UNH', 'JNJ']

def get_symbols_from_file(filename='symbols.txt'):
    """파일에서 종목 리스트 가져오기"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                symbols = [line.strip().upper() for line in f if line.strip()]
            # 파일에서 가져온 종목도 필터링
            return filter_valid_symbols(symbols)
        return []
    except Exception as e:
        print(f"⚠️ 파일에서 종목 리스트 가져오기 실패: {str(e)}")
        return []

def save_symbols_to_file(symbols, filename='symbols.txt'):
    """종목 리스트를 파일로 저장"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for symbol in symbols:
                f.write(f"{symbol}\n")
        print(f"✅ 종목 리스트 저장 완료: {len(symbols)}개 → {filename}")
    except Exception as e:
        print(f"❌ 종목 리스트 저장 실패: {str(e)}")
