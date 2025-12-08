"""
주가 데이터 수집 모듈
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict
import os
import ssl
import config

# SSL 인증서 문제 해결을 위한 환경 변수 설정 (최우선)
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''

# certifi 인증서 경로 찾기 및 설정
try:
    import certifi
    cert_path = certifi.where()
    if cert_path and os.path.exists(cert_path):
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['CURL_CA_BUNDLE'] = cert_path
except:
    # certifi가 없으면 빈 문자열로 설정
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['SSL_CERT_FILE'] = ''
    os.environ['CURL_CA_BUNDLE'] = ''

# SSL 컨텍스트 설정 (전역)
ssl._create_default_https_context = ssl._create_unverified_context

# urllib3 경고 억제
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

# requests 세션 전역 설정
try:
    import requests
    requests.packages.urllib3.disable_warnings()
    # 전역 세션 설정
    session = requests.Session()
    session.verify = False
    # yfinance에 적용
    import yfinance.utils as yf_utils
    if hasattr(yf_utils, '_session'):
        yf_utils._session = session
    if hasattr(yf_utils, 'session'):
        yf_utils.session = session
except:
    pass

# curl_cffi SSL 설정 (yfinance가 curl_cffi를 사용하는 경우)
# curl_cffi는 내부적으로 curl을 사용하므로 환경 변수로만 제어 가능
try:
    # curl_cffi가 SSL 검증을 건너뛰도록 환경 변수 설정
    # 빈 문자열로 설정하면 curl이 기본 인증서 경로를 사용하지 않음
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['SSL_CERT_FILE'] = ''
    
    # curl_cffi의 SSL 검증을 비활성화하기 위한 패치
    try:
        from curl_cffi.requests import Session as CurlSession
        from curl_cffi import Curl
        
        # curl_cffi의 Curl 클래스 패치
        original_init = Curl.__init__
        def patched_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            # SSL 검증 비활성화
            try:
                self.setopt(Curl.OPT_SSL_VERIFYPEER, False)
                self.setopt(Curl.OPT_SSL_VERIFYHOST, False)
            except:
                pass
        
        Curl.__init__ = patched_init
        
        # Session 클래스도 패치
        original_request = CurlSession.request
        def patched_request(self, *args, **kwargs):
            # verify=False 옵션 추가
            kwargs['verify'] = False
            return original_request(self, *args, **kwargs)
        
        CurlSession.request = patched_request
    except Exception as e:
        # curl_cffi 패치 실패해도 계속 진행
        pass
except:
    pass


class DataFetcher:
    """주가 데이터를 수집하는 클래스"""
    
    def __init__(self):
        self.cache = {}
        # yfinance 세션 설정
        self._configure_yfinance()
    
    def _configure_yfinance(self):
        """yfinance SSL 설정 구성"""
        try:
            import yfinance.utils as yf_utils
            import requests
            
            # SSL 검증을 비활성화한 새 세션 생성
            session = requests.Session()
            session.verify = False
            
            # yfinance의 모든 세션 참조 교체
            if hasattr(yf_utils, '_session'):
                yf_utils._session = session
            if hasattr(yf_utils, 'session'):
                yf_utils.session = session
            # 추가 세션 속성 확인
            for attr in dir(yf_utils):
                if 'session' in attr.lower():
                    try:
                        setattr(yf_utils, attr, session)
                    except:
                        pass
                
        except Exception:
            # 설정 실패해도 계속 진행
            pass
    
    def fetch_data(self, symbol: str, interval: str = '1d', period: str = '1y') -> Optional[pd.DataFrame]:
        """
        주가 데이터를 가져옵니다.
        
        Args:
            symbol: 주식 심볼
            interval: 데이터 간격 (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"{symbol}_{interval}_{period}"
        
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        try:
            # curl_cffi SSL 문제를 우회하기 위한 환경 변수 재설정
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['SSL_CERT_FILE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            
            # SSL 검증 비활성화된 세션으로 재설정
            import requests
            import yfinance.utils as yf_utils
            
            # 완전히 새로운 세션 생성 (SSL 검증 완전 비활성화)
            session = requests.Session()
            session.verify = False
            
            # yfinance의 모든 세션 참조 교체
            if hasattr(yf_utils, '_session'):
                yf_utils._session = session
            if hasattr(yf_utils, 'session'):
                yf_utils.session = session
            
            # curl_cffi를 사용하는 경우를 위한 추가 패치
            try:
                # yfinance의 내부 HTTP 클라이언트 패치
                if hasattr(yf_utils, 'session'):
                    # curl_cffi 세션이 있다면 교체 시도
                    pass
            except:
                pass
            
            # yfinance.download 대신 Ticker 사용 (더 안정적)
            # Ticker가 내부적으로 더 나은 에러 핸들링을 함
            ticker = yf.Ticker(symbol)
            
            # 재시도 로직 (API 제한 대응)
            max_retries = 3
            data = None
            for attempt in range(max_retries):
                try:
                    # 각 시도마다 환경 변수 재설정
                    os.environ['CURL_CA_BUNDLE'] = ''
                    os.environ['SSL_CERT_FILE'] = ''
                    
                    # API 제한 회피를 위한 요청 간격 (429 에러 방지)
                    if attempt > 0:
                        import time
                        # 재시도 시 대기 시간 증가 (지수 백오프)
                        wait_time = min(2 ** attempt, 10)  # 최대 10초
                        time.sleep(wait_time)
                    
                    data = ticker.history(period=period, interval=interval)
                    if not data.empty:
                        break
                except Exception as retry_error:
                    error_str = str(retry_error).lower()
                    # API 제한 에러 감지 (429, 403, rate limit 등)
                    is_rate_limit = ('429' in error_str or '403' in error_str or 
                                   'too many' in error_str or 'rate limit' in error_str or
                                   'ratelimit' in error_str)
                    
                    if attempt < max_retries - 1:
                        import time
                        # API 제한인 경우 더 오래 대기
                        if is_rate_limit:
                            wait_time = min(10 * (attempt + 1), 60)  # 최대 60초
                            print(f"⚠️ API 제한 감지, {wait_time}초 대기 중...")
                        else:
                            wait_time = min(2 ** attempt, 10)  # 최대 10초
                        time.sleep(wait_time)
                    else:
                        # 마지막 시도에서도 실패하면 download 시도
                        try:
                            import time
                            if is_rate_limit:
                                time.sleep(10)  # API 제한인 경우 더 오래 대기
                            
                            os.environ['CURL_CA_BUNDLE'] = ''
                            os.environ['SSL_CERT_FILE'] = ''
                            data = yf.download(
                                symbol, 
                                period=period, 
                                interval=interval,
                                progress=False
                            )
                        except:
                            raise retry_error
            
            # 다중 컬럼 인덱스 처리 (download는 MultiIndex를 반환할 수 있음)
            if isinstance(data.columns, pd.MultiIndex):
                # 단일 심볼인 경우 첫 번째 레벨만 사용
                if len(data.columns.levels[0]) == 1:
                    data = data.droplevel(0, axis=1)
                else:
                    data = data.droplevel(1, axis=1)
            
            if data.empty:
                print(f"⚠️ {symbol}에 대한 데이터를 가져올 수 없습니다.")
                return None
            
            # 컬럼명 정규화
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            
            # 캐시에 저장
            self.cache[cache_key] = data.copy()
            
            return data
            
        except Exception as e:
            print(f"❌ {symbol} 데이터 수집 중 오류 발생: {str(e)}")
            return None
    
    def get_multiple_symbols(self, symbols: list, interval: str = '1d', period: str = '1y', 
                            use_batch: bool = True) -> Dict[str, pd.DataFrame]:
        """
        여러 심볼의 데이터를 한번에 가져옵니다 (배치 처리로 속도 향상).
        
        Args:
            symbols: 주식 심볼 리스트
            interval: 데이터 간격
            period: 기간
            use_batch: 배치 처리 사용 여부 (yfinance.download 사용)
        
        Returns:
            {symbol: DataFrame} 딕셔너리
        """
        results = {}
        
        # 배치 처리 (일봉 이상일 때만 가능)
        if use_batch and interval in ['1d', '1wk', '1mo']:
            try:
                # yfinance.download는 여러 종목을 한번에 가져올 수 있음
                os.environ['CURL_CA_BUNDLE'] = ''
                os.environ['SSL_CERT_FILE'] = ''
                
                # 배치로 다운로드 (최대 100개씩)
                batch_size = 100
                for i in range(0, len(symbols), batch_size):
                    batch = symbols[i:i+batch_size]
                    try:
                        data = yf.download(
                            batch,
                            period=period,
                            interval=interval,
                            progress=False,
                            group_by='ticker'
                        )
                        
                        # MultiIndex 처리
                        if isinstance(data.columns, pd.MultiIndex):
                            for symbol in batch:
                                if symbol in data.columns.levels[0]:
                                    symbol_data = data[symbol].copy()
                                    if not symbol_data.empty:
                                        symbol_data.columns = [col.lower().replace(' ', '_') for col in symbol_data.columns]
                                        results[symbol] = symbol_data
                        else:
                            # 단일 종목인 경우
                            if len(batch) == 1:
                                if not data.empty:
                                    data.columns = [col.lower().replace(' ', '_') for col in data.columns]
                                    results[batch[0]] = data
                    except Exception as e:
                        # 배치 실패 시 개별 처리로 폴백
                        for symbol in batch:
                            data = self.fetch_data(symbol, interval, period)
                            if data is not None:
                                results[symbol] = data
                
                return results
                
            except Exception as e:
                # 배치 처리 실패 시 개별 처리로 폴백
                pass
        
        # 개별 처리 (폴백)
        for symbol in symbols:
            data = self.fetch_data(symbol, interval, period)
            if data is not None:
                results[symbol] = data
        return results
    
    def clear_cache(self):
        """캐시를 비웁니다."""
        self.cache.clear()

