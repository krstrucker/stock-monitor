"""종목 정보 가져오기"""
import yfinance as yf
from signal_generator import calculate_score
from data_fetcher import fetch_stock_data, _yf_session

def get_stock_info(symbol):
    """기본 종목 정보"""
    try:
        ticker = yf.Ticker(symbol, session=_yf_session)
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
        ticker = yf.Ticker(symbol, session=_yf_session)
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

