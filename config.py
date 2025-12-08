"""
설정 파일
"""
import os

# API 설정
YAHOO_FINANCE_ENABLED = True

# 분석 설정
# NYSE와 NASDAQ 전체 상장 종목을 자동으로 가져옵니다
# 실패 시 기본 종목 리스트를 사용합니다
def _load_default_symbols():
    """기본 종목 리스트를 로드합니다 (NYSE + NASDAQ 전체 상장 종목 또는 기본 리스트)"""
    try:
        from symbol_fetcher import SymbolFetcher
        fetcher = SymbolFetcher()
        
        print("="*60)
        print("📊 NYSE와 NASDAQ 전체 상장 종목 수집 시작")
        print("="*60)
        
        # NYSE와 NASDAQ 전체 상장 종목 가져오기
        all_symbols = fetcher.get_all_listed_symbols()
        
        if len(all_symbols) > 1000:  # 최소 1000개 이상이면 성공으로 간주
            print(f"\n✅ 총 {len(all_symbols)}개 종목 로드 완료 (NYSE + NASDAQ 전체)")
            print("="*60)
            return all_symbols
        else:
            print(f"\n⚠️ 종목 수가 부족합니다 ({len(all_symbols)}개), 기본 리스트 사용")
            print("="*60)
            return _get_fallback_symbols()
    except Exception as e:
        print(f"⚠️ 종목 리스트 로드 실패: {str(e)}, 기본 리스트 사용")
        return _get_fallback_symbols()

def _get_additional_nasdaq_symbols():
    """추가 NASDAQ 상장 종목 리스트"""
    return [
        # NASDAQ 주요 테크주
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
        'AMD', 'INTC', 'QCOM', 'TXN', 'LRCX', 'KLAC', 'AMAT', 'ASML',
        'NXPI', 'MCHP', 'ON', 'MRVL', 'SWKS', 'QRVO', 'CRUS', 'DIOD',
        # 소프트웨어/SaaS
        'ADBE', 'CRM', 'NOW', 'WDAY', 'ZS', 'CRWD', 'NET', 'SNOW',
        'DDOG', 'MDB', 'ESTC', 'DOCN', 'FROG', 'GTLB', 'TEAM', 'ASAN',
        'COUP', 'BILL', 'DOCU', 'ZM', 'RPD', 'ESTC', 'SPLK', 'QLYS',
        # 인터넷/미디어
        'NFLX', 'ROKU', 'FUBO', 'PARA', 'WBD', 'DIS', 'CMCSA',
        'GOOGL', 'GOOG', 'META', 'SNAP', 'PINS', 'TWTR', 'RDDT',
        # 전자상거래
        'AMZN', 'EBAY', 'ETSY', 'MELI', 'SE', 'SHOP', 'W', 'OSTK',
        # 바이오테크/헬스케어
        'GILD', 'AMGN', 'BIIB', 'REGN', 'VRTX', 'ILMN', 'MRNA', 'BNTX',
        'NVAX', 'SGMO', 'BLUE', 'FOLD', 'RGNX', 'IONS', 'ALKS', 'ALNY',
        # 반도체 장비
        'LRCX', 'KLAC', 'AMAT', 'ASML', 'ONTO', 'UCTT', 'ACMR',
        # 자동차/전기차
        'TSLA', 'LCID', 'RIVN', 'F', 'GM', 'FORD', 'WKHS', 'GOEV',
        # 금융테크
        'HOOD', 'SOFI', 'UPST', 'AFRM', 'LC', 'NU', 'SQ', 'PYPL',
        # 게임/엔터테인먼트
        'EA', 'TTWO', 'ATVI', 'RBLX', 'U', 'DKNG', 'PENN', 'LNW',
        # 클라우드/인프라
        'AMZN', 'MSFT', 'GOOGL', 'ORCL', 'CRM', 'NOW', 'WDAY',
        # 사이버보안
        'CRWD', 'ZS', 'PANW', 'OKTA', 'FTNT', 'QLYS', 'TENB', 'RPD',
        # AI/머신러닝
        'NVDA', 'AMD', 'INTC', 'GOOGL', 'MSFT', 'META', 'TSLA',
        # 로봇/자동화
        'ISRG', 'TER', 'ROK', 'EMR', 'AOS',
        # 소비재
        'COST', 'SBUX', 'NKE', 'LULU', 'ULTA', 'BBWI', 'GPS', 'ANF',
        # 헬스케어 IT
        'TDOC', 'OMCL', 'HIMS', 'LFMD', 'AMWL',
        # 기타 성장주
        'ENPH', 'SEDG', 'RUN', 'ARRY', 'NOVA', 'SPWR', 'CSIQ',
        'PLUG', 'BE', 'FCEL', 'BLDP', 'HYZN'
    ]

def _get_fallback_symbols():
    """기본 종목 리스트 (S&P 500 + NASDAQ 주요 종목)"""
    sp500_symbols = [
        # 대형주 (시가총액 상위)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
        'UNH', 'XOM', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'CVX', 'HD', 'ABBV',
        'AVGO', 'MRK', 'COST', 'PEP', 'ADBE', 'TMO', 'CSCO', 'WMT', 'ACN',
        'ABT', 'NFLX', 'DHR', 'VZ', 'CMCSA', 'NKE', 'PM', 'TXN', 'LIN',
        'NEE', 'DIS', 'HON', 'AMGN', 'RTX', 'INTU', 'IBM', 'AMAT', 'GE',
        'BKNG', 'AXP', 'SYK', 'LOW', 'ADP', 'TJX', 'ISRG', 'DE', 'C',
        'BLK', 'SBUX', 'MMC', 'MO', 'ZTS', 'CI', 'MDT', 'FI', 'PNC',
        'USB', 'GS', 'CL', 'TGT', 'WM', 'DUK', 'SO', 'AON', 'ITW', 'ETN',
        # 테크주
        'AMD', 'INTC', 'QCOM', 'LRCX', 'KLAC', 'CDNS', 'SNPS', 'FTNT',
        'NXPI', 'MCHP', 'ON', 'MRVL', 'CRWD', 'ZS', 'DDOG', 'NET', 'SNOW',
        # 소비재
        'NKE', 'TGT', 'HD', 'LOW', 'TJX', 'ROST', 'DG', 'DLTR', 'BBY',
        # 헬스케어
        'JNJ', 'UNH', 'ABBV', 'TMO', 'ABT', 'DHR', 'ISRG', 'SYK', 'ZTS',
        # 금융
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'AXP', 'COF',
        # 에너지
        'XOM', 'CVX', 'SLB', 'EOG', 'MPC', 'VLO', 'HES',
        # 산업
        'BA', 'CAT', 'DE', 'GE', 'HON', 'RTX', 'LMT', 'NOC', 'GD',
        # 통신
        'VZ', 'T', 'CMCSA', 'DIS', 'NFLX', 'WBD',
        # 유틸리티
        'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'EXC',
        # ETF
        'SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO'
    ]
    
    # NASDAQ 주요 종목 추가
    nasdaq_symbols = [
        # NASDAQ 100
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
        'COST', 'NFLX', 'AMD', 'PEP', 'ADBE', 'CMCSA', 'INTC', 'QCOM',
        'TXN', 'INTU', 'AMGN', 'ISRG', 'VRSK', 'BKNG', 'FISV', 'LRCX',
        'ADP', 'PAYX', 'KLAC', 'CDNS', 'SNPS', 'CTAS', 'FTNT', 'NXPI',
        'MCHP', 'DXCM', 'ODFL', 'FAST', 'CTSH', 'BKR', 'IDXX', 'ANSS',
        'TEAM', 'ROST', 'PCAR', 'ON', 'GEHC', 'CDW', 'CRWD', 'MRVL',
        'ZS', 'DDOG', 'CPRT', 'TTD', 'GFS', 'ENPH', 'ALGN', 'NDAQ',
        'VRSN', 'CSGP', 'WBD', 'ILMN', 'DLTR', 'EXPE', 'XEL', 'EA',
        # 추가 NASDAQ 성장주
        'HOOD', 'SOFI', 'UPST', 'AFRM', 'LC', 'NU', 'SQ', 'PYPL',
        'RBLX', 'U', 'DKNG', 'PENN', 'LNW', 'LCID', 'RIVN', 'F',
        'MELI', 'SE', 'SHOP', 'W', 'OSTK', 'ETSY', 'EBAY',
        'TDOC', 'OMCL', 'HIMS', 'LFMD', 'AMWL',
        'ENPH', 'SEDG', 'RUN', 'ARRY', 'NOVA', 'SPWR', 'CSIQ',
        'PLUG', 'BE', 'FCEL', 'BLDP', 'HYZN',
        'GILD', 'BIIB', 'REGN', 'VRTX', 'MRNA', 'BNTX', 'NVAX',
        'SGMO', 'BLUE', 'FOLD', 'RGNX', 'IONS', 'ALKS', 'ALNY',
        'NOW', 'WDAY', 'MDB', 'ESTC', 'DOCN', 'FROG', 'GTLB', 'ASAN',
        'COUP', 'BILL', 'DOCU', 'ZM', 'RPD', 'SPLK', 'QLYS',
        'PANW', 'OKTA', 'TENB', 'ASML', 'ONTO', 'UCTT', 'ACMR',
        'SWKS', 'QRVO', 'CRUS', 'DIOD', 'WKHS', 'GOEV'
    ]
    
    # 중복 제거하면서 합치기
    all_symbols = list(dict.fromkeys(sp500_symbols + nasdaq_symbols))
    return all_symbols

# DEFAULT_SYMBOLS 자동 로드
DEFAULT_SYMBOLS = _load_default_symbols()

# 신호 레벨 설정
SIGNAL_LEVELS = {
    'STRONG_BUY': {
        'name': '강한 매수',
        'score_range': (8, 10),
        'color': 'green',
        'description': '여러 지표가 동시에 긍정적이며 높은 수익 기대'
    },
    'BUY': {
        'name': '매수',
        'score_range': (5, 7),
        'color': 'blue',
        'description': '일부 지표가 긍정적이며 수익 가능성 있음'
    },
    'WATCH': {
        'name': '관망 매수',
        'score_range': (3, 4),
        'color': 'yellow',
        'description': '잠재적 기회가 있으나 추가 확인 필요'
    }
}

# 시간프레임 설정
TIMEFRAMES = {
    'day_trading': {
        'name': '데이트레이딩',
        'interval': '5m',
        'period': '5d',
        'lookback_days': 5
    },
    'short_swing': {
        'name': '단기 스윙',
        'interval': '1d',
        'period': '3mo',
        'lookback_days': 20
    },
    'long_swing': {
        'name': '중장기 스윙',
        'interval': '1d',
        'period': '1y',
        'lookback_days': 60
    }
}

# 기술적 지표 가중치
INDICATOR_WEIGHTS = {
    'rsi': 0.15,
    'macd': 0.20,
    'moving_average': 0.20,
    'bollinger_bands': 0.15,
    'volume': 0.15,
    'momentum': 0.15
}

# RSI 설정
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# MACD 설정
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# 이동평균선 설정
MA_SHORT = 20
MA_LONG = 50

# 볼린저 밴드 설정
BB_PERIOD = 20
BB_STD = 2

