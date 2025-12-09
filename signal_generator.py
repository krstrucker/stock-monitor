"""매수 신호 생성"""
import pandas as pd
import numpy as np
import ta
from datetime import datetime

# pandas의 isna 함수 사용
pd_isna = pd.isna

def calculate_score(data):
    """종목 점수 계산 (0-10점)"""
    if data is None or data.empty or len(data) < 20:
        return 0.0
    
    try:
        score = 0.0
        
        # RSI (상대강도지수)
        try:
            rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
            if not rsi.empty and not pd_isna(rsi.iloc[-1]):
                current_rsi = rsi.iloc[-1]
                if 30 <= current_rsi <= 70:  # 과매수/과매도 구간 제외
                    score += 1.0
                if 40 <= current_rsi <= 60:  # 중립 구간
                    score += 0.5
        except:
            pass
        
        # MACD
        try:
            macd = ta.trend.MACD(data['Close'])
            macd_line = macd.macd()
            signal_line = macd.macd_signal()
            if not macd_line.empty and not signal_line.empty:
                if not pd_isna(macd_line.iloc[-1]) and not pd_isna(signal_line.iloc[-1]):
                    if macd_line.iloc[-1] > signal_line.iloc[-1]:  # 골든크로스
                        score += 1.5
        except:
            pass
        
        # 이동평균선
        try:
            ma20 = data['Close'].rolling(window=20).mean()
            if len(data) >= 50:
                ma50 = data['Close'].rolling(window=50).mean()
                if not ma20.empty and not ma50.empty:
                    if not pd_isna(ma20.iloc[-1]) and not pd_isna(ma50.iloc[-1]):
                        if ma20.iloc[-1] > ma50.iloc[-1]:  # 단기 > 장기
                            score += 1.0
            if not ma20.empty and not pd_isna(ma20.iloc[-1]):
                if data['Close'].iloc[-1] > ma20.iloc[-1]:  # 현재가 > 단기
                    score += 1.0
        except:
            pass
        
        # 볼린저 밴드
        try:
            bb = ta.volatility.BollingerBands(data['Close'], window=20)
            bb_upper = bb.bollinger_hband()
            bb_lower = bb.bollinger_lband()
            if not bb_lower.empty and not pd_isna(bb_lower.iloc[-1]):
                if data['Close'].iloc[-1] <= bb_lower.iloc[-1]:  # 하단 터치
                    score += 1.5
        except:
            pass
        
        # 거래량
        try:
            volume_ma = data['Volume'].rolling(window=20).mean()
            if not volume_ma.empty and not pd_isna(volume_ma.iloc[-1]):
                if data['Volume'].iloc[-1] > volume_ma.iloc[-1] * 1.2:  # 거래량 증가
                    score += 1.0
        except:
            pass
        
        # 가격 추세
        try:
            if len(data) >= 5:
                recent_trend = (data['Close'].iloc[-1] - data['Close'].iloc[-5]) / data['Close'].iloc[-5]
                if recent_trend > 0:  # 상승 추세
                    score += 1.0
        except:
            pass
        
        # 최대 10점으로 제한
        return min(score, 10.0)
    except Exception as e:
        # 조용히 실패 (로그는 monitor.py에서 출력)
        return 0.0

def generate_signal(symbol, data):
    """기술적 분석 기반 매수 신호 생성 (점수만 반환)"""
    if data is None or data.empty:
        return None
    
    try:
        score = calculate_score(data)
        current_price = data['Close'].iloc[-1]
        
        # 점수가 있으면 항상 반환 (7.5점 미만이어도)
        return {
            'symbol': symbol,
            'level': 'BUY' if score >= 7.5 else 'WATCH',
            'score': round(score, 2),
            'price': round(current_price, 2),
            'date': datetime.now().isoformat(),
            'method': 'technical'
        }
    except Exception as e:
        return None

def get_technical_score_only(symbol, data):
    """기술적 분석 점수만 반환 (다른 방법론과 비교용)"""
    try:
        score = calculate_score(data)
        return round(score, 2)
    except:
        return 0.0

