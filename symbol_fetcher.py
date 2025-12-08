"""
주식 심볼 리스트를 가져오는 모듈
S&P 500, NASDAQ 100 등의 종목 리스트를 자동으로 가져옵니다.
"""
import yfinance as yf
import pandas as pd
from typing import List, Optional
import requests
import os
import ssl

# SSL 설정
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context


class SymbolFetcher:
    """주식 심볼 리스트를 가져오는 클래스"""
    
    def __init__(self):
        pass
    
    def get_sp500_symbols(self) -> List[str]:
        """
        S&P 500 종목 리스트를 가져옵니다.
        
        Returns:
            S&P 500 종목 심볼 리스트
        """
        try:
            # Wikipedia에서 S&P 500 리스트 가져오기
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            
            # SSL 검증 비활성화
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            session = requests.Session()
            session.verify = False
            
            # HTML 가져오기
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            # pandas로 HTML 테이블 파싱
            tables = pd.read_html(response.text)
            sp500_table = tables[0]
            
            # 심볼 컬럼 추출
            symbols = sp500_table['Symbol'].tolist()
            
            # 심볼 정리 (점 제거 등)
            symbols = [s.replace('.', '-') for s in symbols if pd.notna(s)]
            
            return symbols
            
        except Exception as e:
            print(f"⚠️ S&P 500 리스트 가져오기 실패: {str(e)}")
            # 대체 방법: 기본 리스트 반환
            return self._get_default_sp500_symbols()
    
    def _get_default_sp500_symbols(self) -> List[str]:
        """기본 S&P 500 종목 리스트 (주요 종목 - 약 200개)"""
        return [
            # 대형주 (시가총액 상위)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'UNH', 'XOM', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'CVX', 'HD', 'ABBV',
            'AVGO', 'MRK', 'COST', 'PEP', 'ADBE', 'TMO', 'CSCO', 'WMT', 'ACN',
            'ABT', 'NFLX', 'DHR', 'VZ', 'CMCSA', 'NKE', 'PM', 'TXN', 'LIN',
            'NEE', 'DIS', 'HON', 'AMGN', 'RTX', 'INTU', 'IBM', 'AMAT', 'GE',
            'BKNG', 'AXP', 'SYK', 'LOW', 'ADP', 'TJX', 'ISRG', 'DE', 'C',
            'BLK', 'SBUX', 'MMC', 'MO', 'ZTS', 'CI', 'MDT', 'FI', 'PNC',
            'USB', 'GS', 'CL', 'TGT', 'WM', 'DUK', 'SO', 'AON', 'ITW', 'ETN',
            # 추가 대형주
            'LMT', 'NOC', 'GD', 'BA', 'CAT', 'HES', 'SLB', 'EOG', 'MPC', 'VLO',
            'BAC', 'WFC', 'MS', 'COF', 'SCHW', 'TFC', 'CFG', 'KEY', 'ZION',
            'T', 'TMUS', 'LUMN', 'VZ', 'CMCSA', 'CHTR', 'DISCA', 'FOXA',
            'NFLX', 'WBD', 'PARA', 'ROKU', 'FUBO',
            # 테크주
            'AMD', 'INTC', 'QCOM', 'LRCX', 'KLAC', 'CDNS', 'SNPS', 'FTNT',
            'NXPI', 'MCHP', 'ON', 'MRVL', 'CRWD', 'ZS', 'DDOG', 'NET', 'SNOW',
            'PANW', 'OKTA', 'S', 'VZ', 'T', 'LUMN',
            # 소비재
            'NKE', 'TGT', 'HD', 'LOW', 'TJX', 'ROST', 'DG', 'DLTR', 'BBY',
            'BBWI', 'GPS', 'ANF', 'AEO', 'URBN', 'DKS', 'HIBB',
            # 헬스케어
            'JNJ', 'UNH', 'ABBV', 'TMO', 'ABT', 'DHR', 'ISRG', 'SYK', 'ZTS',
            'BSX', 'EW', 'HCA', 'HUM', 'CNC', 'MOH', 'CI', 'ANTM',
            # 금융
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'AXP', 'COF',
            'SCHW', 'TFC', 'CFG', 'KEY', 'ZION', 'HBAN', 'MTB', 'FITB',
            # 에너지
            'XOM', 'CVX', 'SLB', 'EOG', 'MPC', 'VLO', 'HES', 'COP', 'OVV',
            'FANG', 'MRO', 'DVN', 'CTRA', 'PR', 'NOV',
            # 산업
            'BA', 'CAT', 'DE', 'GE', 'HON', 'RTX', 'LMT', 'NOC', 'GD',
            'TXT', 'PH', 'EMR', 'ETN', 'IR', 'GGG', 'AOS',
            # 통신
            'VZ', 'T', 'CMCSA', 'DIS', 'NFLX', 'WBD', 'CHTR', 'LUMN',
            # 유틸리티
            'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'EXC', 'XEL', 'ES', 'ED',
            'ETR', 'FE', 'PEG', 'AEE', 'CMS', 'CNP',
            # 소재
            'LIN', 'APD', 'ECL', 'SHW', 'PPG', 'DD', 'DOW', 'FCX', 'NEM',
            # 부동산
            'AMT', 'PLD', 'EQIX', 'PSA', 'WELL', 'VICI', 'SPG', 'O',
            # ETF
            'SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO', 'IVV', 'SPLG'
        ]
    
    def get_nasdaq100_symbols(self) -> List[str]:
        """
        NASDAQ 100 종목 리스트를 가져옵니다.
        
        Returns:
            NASDAQ 100 종목 심볼 리스트
        """
        try:
            # Wikipedia에서 NASDAQ 100 리스트 가져오기
            url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
            
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            session = requests.Session()
            session.verify = False
            
            # HTML 가져오기
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            # pandas로 HTML 테이블 파싱
            tables = pd.read_html(response.text)
            
            # NASDAQ 100 테이블 찾기
            for table in tables:
                if 'Ticker' in table.columns or 'Symbol' in table.columns:
                    if 'Ticker' in table.columns:
                        symbols = table['Ticker'].tolist()
                    else:
                        symbols = table['Symbol'].tolist()
                    
                    symbols = [s.replace('.', '-') for s in symbols if pd.notna(s)]
                    return symbols
            
            return []
            
        except Exception as e:
            print(f"⚠️ NASDAQ 100 리스트 가져오기 실패: {str(e)}")
            return self._get_default_nasdaq100_symbols()
    
    def _get_default_nasdaq100_symbols(self) -> List[str]:
        """기본 NASDAQ 100 종목 리스트 (주요 종목만)"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
            'COST', 'NFLX', 'AMD', 'PEP', 'ADBE', 'CMCSA', 'INTC', 'QCOM',
            'TXN', 'INTU', 'AMGN', 'ISRG', 'VRSK', 'BKNG', 'FISV', 'LRCX',
            'ADP', 'PAYX', 'KLAC', 'CDNS', 'SNPS', 'CTAS', 'FTNT', 'NXPI',
            'MCHP', 'DXCM', 'ODFL', 'FAST', 'CTSH', 'BKR', 'IDXX', 'ANSS',
            'TEAM', 'ROST', 'PCAR', 'ON', 'GEHC', 'CDW', 'CRWD', 'MRVL',
            'ZS', 'DDOG', 'CPRT', 'TTD', 'GFS', 'ENPH', 'ALGN', 'NDAQ',
            'VRSN', 'CSGP', 'WBD', 'ILMN', 'DLTR', 'EXPE', 'XEL', 'EA',
            'FANG', 'ZS', 'MELI', 'LCID', 'RIVN', 'PTON', 'HOOD', 'SOFI'
        ]
    
    def get_dow30_symbols(self) -> List[str]:
        """
        Dow Jones 30 종목 리스트를 가져옵니다.
        
        Returns:
            Dow 30 종목 심볼 리스트
        """
        return [
            'AAPL', 'MSFT', 'UNH', 'GS', 'HD', 'CAT', 'MCD', 'AMGN', 'V',
            'HON', 'TRV', 'AXP', 'IBM', 'JPM', 'PG', 'JNJ', 'WMT', 'CVX',
            'MRK', 'DIS', 'BA', 'DOW', 'NKE', 'MMM', 'VZ', 'CSCO', 'INTC',
            'WBA', 'AMZN', 'CRM'
        ]
    
    def get_nasdaq_all_symbols(self) -> List[str]:
        """
        NASDAQ 전체 상장 종목 리스트를 가져옵니다.
        
        Returns:
            NASDAQ 전체 상장 종목 심볼 리스트
        """
        try:
            # NASDAQ 공식 사이트에서 전체 종목 리스트 가져오기
            url = 'https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&offset=0&download=true'
            
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            session = requests.Session()
            session.verify = False
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'rows' in data['data']:
                symbols = [row['symbol'] for row in data['data']['rows'] if 'symbol' in row]
                # 심볼 정리
                symbols = [s.replace('.', '-') for s in symbols if s and pd.notna(s)]
                return symbols
            
            return []
            
        except Exception as e:
            print(f"⚠️ NASDAQ 전체 종목 리스트 가져오기 실패: {str(e)}")
            # 대체 방법: Wikipedia에서 NASDAQ 상장 종목 리스트 시도
            try:
                return self._get_nasdaq_from_wikipedia()
            except:
                return []
    
    def _get_nasdaq_from_wikipedia(self) -> List[str]:
        """Wikipedia에서 NASDAQ 상장 종목 리스트 가져오기 (대체 방법)"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_NASDAQ_listed_securities'
            
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            session = requests.Session()
            session.verify = False
            
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            tables = pd.read_html(response.text)
            
            symbols = []
            for table in tables:
                if 'Symbol' in table.columns or 'Ticker' in table.columns:
                    col = 'Symbol' if 'Symbol' in table.columns else 'Ticker'
                    table_symbols = table[col].tolist()
                    symbols.extend([s.replace('.', '-') for s in table_symbols if pd.notna(s)])
            
            return list(set(symbols))  # 중복 제거
            
        except Exception as e:
            print(f"⚠️ Wikipedia에서 NASDAQ 리스트 가져오기 실패: {str(e)}")
            return []
    
    def get_nyse_all_symbols(self) -> List[str]:
        """
        NYSE 전체 상장 종목 리스트를 가져옵니다.
        
        Returns:
            NYSE 전체 상장 종목 심볼 리스트
        """
        try:
            # 방법 1: NYSE 공식 API 시도
            try:
                # NYSE는 직접 API가 제한적이므로 다른 방법 사용
                pass
            except:
                pass
            
            # 방법 2: Wikipedia에서 NYSE 상장 종목 리스트 가져오기
            symbols = self._get_nyse_from_wikipedia()
            if symbols and len(symbols) > 100:
                return symbols
            
            # 방법 3: S&P 500, 400, 600 등에서 NYSE 종목 추출 (대부분이 NYSE)
            sp_symbols = self.get_sp500_symbols()
            if sp_symbols:
                return sp_symbols  # 임시로 S&P 500 종목 반환 (대부분 NYSE)
            
            return []
            
        except Exception as e:
            print(f"⚠️ NYSE 전체 종목 리스트 가져오기 실패: {str(e)}")
            return []
    
    def _get_nyse_from_wikipedia(self) -> List[str]:
        """Wikipedia에서 NYSE 상장 종목 리스트 가져오기"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            session = requests.Session()
            session.verify = False
            
            # 여러 Wikipedia 페이지에서 NYSE 종목 수집
            urls = [
                'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
                'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies',
                'https://en.wikipedia.org/wiki/List_of_S%26P_600_companies'
            ]
            
            symbols = []
            for url in urls:
                try:
                    response = session.get(url, timeout=30)
                    response.raise_for_status()
                    
                    tables = pd.read_html(response.text)
                    for table in tables:
                        if 'Symbol' in table.columns:
                            table_symbols = table['Symbol'].tolist()
                            symbols.extend([s.replace('.', '-') for s in table_symbols if pd.notna(s)])
                except:
                    continue
            
            return list(set(symbols))  # 중복 제거
            
        except Exception as e:
            print(f"⚠️ Wikipedia에서 NYSE 리스트 가져오기 실패: {str(e)}")
            return []
    
    def get_all_listed_symbols(self) -> List[str]:
        """
        NYSE와 NASDAQ 전체 상장 종목 리스트를 가져옵니다.
        
        Returns:
            NYSE + NASDAQ 전체 상장 종목 심볼 리스트 (중복 제거)
        """
        print("📊 NYSE와 NASDAQ 전체 상장 종목 수집 중...")
        
        all_symbols = []
        
        # NASDAQ 전체 종목 (주요 소스)
        print("  - NASDAQ 종목 수집 중...")
        nasdaq_symbols = self.get_nasdaq_all_symbols()
        if nasdaq_symbols:
            all_symbols.extend(nasdaq_symbols)
            print(f"    ✅ NASDAQ: {len(nasdaq_symbols)}개 종목")
        else:
            print(f"    ⚠️ NASDAQ 종목 수집 실패")
        
        # NYSE 전체 종목
        print("  - NYSE 종목 수집 중...")
        nyse_symbols = self.get_nyse_all_symbols()
        if nyse_symbols:
            # 중복 제거하면서 추가
            for symbol in nyse_symbols:
                if symbol not in all_symbols:
                    all_symbols.append(symbol)
            print(f"    ✅ NYSE: {len(nyse_symbols)}개 종목 (중복 제외: {len([s for s in nyse_symbols if s not in nasdaq_symbols])}개 추가)")
        else:
            print(f"    ⚠️ NYSE 종목 수집 실패 (NASDAQ 종목만 사용)")
        
        # 중복 제거 (이미 위에서 처리했지만 안전을 위해)
        unique_symbols = list(dict.fromkeys(all_symbols))
        
        print(f"✅ 총 {len(unique_symbols)}개 종목 수집 완료 (NYSE + NASDAQ)")
        
        return unique_symbols
    
    def get_symbols_by_index(self, index_name: str) -> List[str]:
        """
        인덱스 이름으로 종목 리스트를 가져옵니다.
        
        Args:
            index_name: 'sp500', 'nasdaq100', 'dow30', 'nasdaq_all', 'nyse_all', 'all' 중 하나
        
        Returns:
            종목 심볼 리스트
        """
        index_name = index_name.lower()
        
        if index_name == 'sp500' or index_name == 'sp_500':
            return self.get_sp500_symbols()
        elif index_name == 'nasdaq100' or index_name == 'nasdaq_100':
            return self.get_nasdaq100_symbols()
        elif index_name == 'dow30' or index_name == 'dow_30':
            return self.get_dow30_symbols()
        elif index_name == 'nasdaq_all' or index_name == 'nasdaq':
            return self.get_nasdaq_all_symbols()
        elif index_name == 'nyse_all' or index_name == 'nyse':
            return self.get_nyse_all_symbols()
        elif index_name == 'all' or index_name == 'all_listed':
            return self.get_all_listed_symbols()
        else:
            print(f"⚠️ 알 수 없는 인덱스: {index_name}")
            return []

