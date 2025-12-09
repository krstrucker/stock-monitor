"""종목 리스트 가져오기"""
import yfinance as yf
import pandas as pd
import requests
import time
import os

def get_all_symbols():
    """모든 미국 주식 종목 리스트 가져오기"""
    try:
        symbols = []
        
        # 방법 1: NASDAQ API 사용
        try:
            nasdaq_url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&offset=0&download=true"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            response = requests.get(nasdaq_url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'rows' in data['data']:
                    for row in data['data']['rows']:
                        symbol = row.get('symbol', '').strip().upper()
                        if symbol and len(symbol) <= 5 and '.' not in symbol:
                            symbols.append(symbol)
                    print(f"✅ NASDAQ API에서 {len(symbols)}개 종목 가져옴")
        except Exception as e:
            print(f"⚠️ NASDAQ API 실패: {str(e)}")
        
        # 방법 2: S&P 500 종목 리스트 (백업)
        if len(symbols) < 100:
            try:
                sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
                tables = pd.read_html(sp500_url)
                sp500_table = tables[0]
                sp500_symbols = sp500_table['Symbol'].tolist()
                symbols.extend(sp500_symbols)
                print(f"✅ S&P 500에서 {len(sp500_symbols)}개 종목 추가")
            except Exception as e:
                print(f"⚠️ S&P 500 가져오기 실패: {str(e)}")
        
        # 방법 3: 주요 종목 리스트 (최종 백업)
        if len(symbols) < 50:
            major_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'BRK-A',
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
            symbols.extend(major_symbols)
            print(f"⚠️ 백업 종목 리스트 사용: {len(major_symbols)}개 추가")
        
        # 중복 제거 및 정렬
        symbols = sorted(list(set([s.upper() for s in symbols if s and len(s) <= 5])))
        
        print(f"✅ 종목 리스트 로드 완료: 총 {len(symbols)}개")
        return symbols
        
    except Exception as e:
        print(f"❌ 종목 리스트 가져오기 실패: {str(e)}")
        # 최소한의 종목 리스트라도 반환
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'V', 'UNH', 'JNJ']

def get_symbols_from_file(filename='symbols.txt'):
    """파일에서 종목 리스트 가져오기"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            symbols = [line.strip() for line in f if line.strip()]
        return symbols
    except:
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
