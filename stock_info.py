"""종목 정보 가져오기"""
import yfinance as yf
import requests
from signal_generator import calculate_score
from data_fetcher import fetch_stock_data

def get_stock_info(symbol):
    """기본 종목 정보 - 직접 API 호출"""
    try:
        # 직접 Yahoo Finance API 호출 시도
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
                    meta = result['meta']
                    return {
                        'name': meta.get('longName', symbol),
                        'sector': meta.get('sector', 'N/A'),
                        'industry': meta.get('industry', 'N/A'),
                        'marketCap': meta.get('marketCap', 0),
                        'currentPrice': meta.get('regularMarketPrice', 0)
                    }
    except:
        pass
    
    # Fallback: yfinance
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'marketCap': info.get('marketCap', 0),
            'currentPrice': info.get('currentPrice', 0)
        }
    except:
        return {
            'name': symbol,
            'sector': 'N/A',
            'industry': 'N/A',
            'marketCap': 0,
            'currentPrice': 0
        }

def get_recommendation_reason(symbol, signal_data):
    """추천 이유 생성"""
    try:
        data = fetch_stock_data(symbol)
        if data is None or data.empty:
            return "데이터 부족"
        
        reasons = []
        
        # RSI 분석
        import ta
        rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        if not rsi.empty:
            current_rsi = rsi.iloc[-1]
            if current_rsi < 40:
                reasons.append("RSI가 과매도 구간에 있어 반등 가능성")
            elif 40 <= current_rsi <= 60:
                reasons.append("RSI가 적정 수준")
        
        # MACD 분석
        macd = ta.trend.MACD(data['Close'])
        macd_line = macd.macd()
        signal_line = macd.macd_signal()
        if not macd_line.empty and not signal_line.empty:
            if macd_line.iloc[-1] > signal_line.iloc[-1]:
                reasons.append("MACD 골든크로스 발생")
        
        # 이동평균선
        ma20 = data['Close'].rolling(window=20).mean()
        if not ma20.empty:
            if data['Close'].iloc[-1] > ma20.iloc[-1]:
                reasons.append("20일 이동평균선 위에 위치")
        
        return "; ".join(reasons) if reasons else "기술적 지표가 매수 신호를 보임"
    except:
        return "기술적 분석 결과 매수 추천"

def get_recent_news(symbol, limit=5):
    """최근 뉴스"""
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news[:limit]
        
        news_list = []
        for item in news:
            news_list.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'publisher': item.get('publisher', ''),
                'published': item.get('providerPublishTime', 0)
            })
        
        return news_list
    except:
        return []

def get_pros_cons(symbol, signal_data):
    """장단점"""
    score = signal_data.get('score', 0)
    price = signal_data.get('price', 0)
    
    pros = []
    cons = []
    
    if score >= 8.0:
        pros.append("매우 높은 신호 점수")
    elif score >= 7.5:
        pros.append("높은 신호 점수")
    
    if price < 10:
        pros.append("저가 종목으로 접근 용이")
        cons.append("저가 종목은 변동성이 클 수 있음")
    
    if not pros:
        pros.append("기술적 지표가 긍정적")
    
    if not cons:
        cons.append("시장 상황에 따라 변동 가능")
    
    return {
        'pros': pros,
        'cons': cons
    }

