"""
종목 필터링 모듈
시가총액, 거래량 등 기준으로 종목을 필터링합니다.
"""
import yfinance as yf
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def get_market_cap(symbol: str) -> Optional[float]:
    """
    종목의 시가총액을 가져옵니다.
    
    Args:
        symbol: 주식 심볼
    
    Returns:
        시가총액 (달러), 실패 시 None
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        market_cap = info.get('marketCap')
        if market_cap and market_cap > 0:
            return float(market_cap)
    except:
        pass
    return None


def filter_by_market_cap(symbols: List[str], top_n: int = 1000, 
                         min_market_cap: Optional[float] = None,
                         max_workers: int = 20) -> List[str]:
    """
    시가총액 기준으로 종목을 필터링합니다.
    
    Args:
        symbols: 종목 리스트
        top_n: 상위 N개 선택
        min_market_cap: 최소 시가총액 (달러, 선택사항)
        max_workers: 동시 실행 스레드 수
    
    Returns:
        필터링된 종목 리스트 (시가총액 높은 순)
    """
    print(f"\n{'='*60}")
    print(f"📊 시가총액 기준 종목 필터링 시작")
    print(f"   전체 종목: {len(symbols)}개")
    print(f"   목표: 상위 {top_n}개")
    if min_market_cap:
        print(f"   최소 시가총액: ${min_market_cap:,.0f}")
    print(f"{'='*60}\n")
    
    symbol_caps = {}
    failed_symbols = []
    
    def fetch_cap(symbol):
        cap = get_market_cap(symbol)
        if cap:
            return (symbol, cap)
        else:
            return (symbol, None)
    
    # 병렬로 시가총액 가져오기
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_cap, symbol): symbol for symbol in symbols}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            symbol, cap = future.result()
            
            if cap:
                symbol_caps[symbol] = cap
            else:
                failed_symbols.append(symbol)
            
            if completed % 100 == 0:
                print(f"   진행: {completed}/{len(symbols)} ({len(symbol_caps)}개 성공)")
    
    print(f"\n✅ 시가총액 정보 수집 완료: {len(symbol_caps)}개 성공, {len(failed_symbols)}개 실패")
    
    # 시가총액 기준 정렬
    sorted_symbols = sorted(symbol_caps.items(), key=lambda x: x[1], reverse=True)
    
    # 최소 시가총액 필터링
    if min_market_cap:
        sorted_symbols = [(s, cap) for s, cap in sorted_symbols if cap >= min_market_cap]
    
    # 상위 N개 선택
    filtered_symbols = [symbol for symbol, cap in sorted_symbols[:top_n]]
    
    # 실패한 종목 중 일부 추가 (시가총액 정보가 없어도 포함)
    remaining = top_n - len(filtered_symbols)
    if remaining > 0 and failed_symbols:
        filtered_symbols.extend(failed_symbols[:remaining])
    
    print(f"✅ 최종 선택: {len(filtered_symbols)}개 종목")
    if filtered_symbols:
        print(f"   상위 10개: {', '.join(filtered_symbols[:10])}")
    
    return filtered_symbols


def filter_by_index_priority(symbols: List[str], top_n: int = 1000) -> List[str]:
    """
    인덱스 우선순위 기준으로 종목을 필터링합니다.
    S&P 500, NASDAQ 100, Dow 30 종목을 우선 선택합니다.
    
    Args:
        symbols: 종목 리스트
        top_n: 최종 선택할 종목 수
    
    Returns:
        필터링된 종목 리스트
    """
    try:
        from symbol_fetcher import SymbolFetcher
        fetcher = SymbolFetcher()
        
        # 인덱스 종목 가져오기
        sp500 = set(fetcher.get_sp500_symbols())
        nasdaq100 = set(fetcher.get_nasdaq100_symbols())
        dow30 = set(fetcher.get_dow30_symbols())
        
        # 우선순위별로 분류
        priority_1 = list(dow30)  # Dow 30 (최우선)
        priority_2 = list(sp500 - dow30)  # S&P 500 (Dow 제외)
        priority_3 = list(nasdaq100 - sp500)  # NASDAQ 100 (S&P 500 제외)
        
        # 나머지 종목
        all_index_symbols = dow30 | sp500 | nasdaq100
        others = [s for s in symbols if s not in all_index_symbols]
        
        # 우선순위대로 선택
        selected = []
        selected.extend(priority_1[:top_n])
        if len(selected) < top_n:
            selected.extend(priority_2[:top_n - len(selected)])
        if len(selected) < top_n:
            selected.extend(priority_3[:top_n - len(selected)])
        if len(selected) < top_n:
            selected.extend(others[:top_n - len(selected)])
        
        print(f"\n✅ 인덱스 우선순위 기준 필터링 완료")
        print(f"   Dow 30: {len(priority_1)}개")
        print(f"   S&P 500: {len(priority_2)}개")
        print(f"   NASDAQ 100: {len(priority_3)}개")
        print(f"   기타: {len(others)}개")
        print(f"   최종 선택: {len(selected)}개 종목")
        
        return selected[:top_n]
        
    except Exception as e:
        print(f"⚠️ 인덱스 우선순위 필터링 실패: {str(e)}")
        # 실패 시 단순히 앞에서부터 선택
        return symbols[:top_n]

