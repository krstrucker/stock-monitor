"""매수 신호 생성"""
import pandas as pd
import numpy as np
import ta
from datetime import datetime

def calculate_score(data):
    """종목 점수 계산 (0-10점)"""
    if data is None or data.empty or len(data) < 20:
        return 0.0
    
    try:
        score = 0.0
        
        # RSI (상대강도지수)
        rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        if not rsi.empty:
            current_rsi = rsi.iloc[-1]
            if 30 <= current_rsi <= 70:  # 과매수/과매도 구간 제외
                score += 1.0
            if 40 <= current_rsi <= 60:  # 중립 구간
                score += 0.5
        
        # MACD
        macd = ta.trend.MACD(data['Close'])
        macd_line = macd.macd()
        signal_line = macd.macd_signal()
        if not macd_line.empty and not signal_line.empty:
            if macd_line.iloc[-1] > signal_line.iloc[-1]:  # 골든크로스
                score += 1.5
        
        # 이동평균선
        ma20 = data['Close'].rolling(window=20).mean()
        ma50 = data['Close'].rolling(window=50).mean()
        if not ma20.empty and not ma50.empty:
            if ma20.iloc[-1] > ma50.iloc[-1]:  # 단기 > 장기
                score += 1.0
            if data['Close'].iloc[-1] > ma20.iloc[-1]:  # 현재가 > 단기
                score += 1.0
        
        # 볼린저 밴드
        bb = ta.volatility.BollingerBands(data['Close'], window=20)
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()
        if not bb_lower.empty:
            if data['Close'].iloc[-1] <= bb_lower.iloc[-1]:  # 하단 터치
                score += 1.5
        
        # 거래량
        volume_ma = data['Volume'].rolling(window=20).mean()
        if not volume_ma.empty:
            if data['Volume'].iloc[-1] > volume_ma.iloc[-1] * 1.2:  # 거래량 증가
                score += 1.0
        
        # 가격 추세
        if len(data) >= 5:
            recent_trend = (data['Close'].iloc[-1] - data['Close'].iloc[-5]) / data['Close'].iloc[-5]
            if recent_trend > 0:  # 상승 추세
                score += 1.0
        
        # 최대 10점으로 제한
        return min(score, 10.0)
    except Exception as e:
        print(f"점수 계산 오류: {str(e)}")
        return 0.0

def generate_signal(symbol, data):
    """매수 신호 생성"""
    if data is None or data.empty:
        return None
    
    score = calculate_score(data)
    
    if score >= 7.5:  # 7.5점 이상만 신호
        current_price = data['Close'].iloc[-1]
        return {
            'symbol': symbol,
            'level': 'BUY',
            'score': round(score, 2),
            'price': round(current_price, 2),
            'date': datetime.now().isoformat()
        }
    
    return None

