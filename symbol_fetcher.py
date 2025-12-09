"""종목 리스트 가져오기"""
import yfinance as yf
import time

def get_all_symbols():
    """모든 미국 주식 종목 리스트 가져오기"""
    try:
        # NASDAQ + NYSE 종목 가져오기
        nasdaq = yf.Tickers("^IXIC")
        # 실제로는 NASDAQ과 NYSE의 전체 종목 리스트를 가져와야 하지만
        # yfinance로는 직접 가져올 수 없으므로 다른 방법 사용
        
        # 대안: NASDAQ과 NYSE의 주요 종목들을 직접 리스트로 제공
        # 실제로는 외부 API나 파일에서 가져와야 함
        
        # 임시로 빈 리스트 반환 (실제 구현 필요)
        return []
    except Exception as e:
        print(f"종목 리스트 가져오기 실패: {str(e)}")
        return []

def get_symbols_from_file():
    """파일에서 종목 리스트 가져오기 (백업 방법)"""
    try:
        # 실제로는 NASDAQ/NYSE 종목 리스트 파일이 있어야 함
        return []
    except:
        return []

