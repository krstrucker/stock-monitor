"""
매수 신호 생성 모듈
3종류의 매수 신호를 생성합니다:
1. 강한 매수 (STRONG_BUY): 점수 8-10
2. 매수 (BUY): 점수 5-7
3. 관망 매수 (WATCH): 점수 3-4
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import ta
import config


class SignalGenerator:
    """매수 신호를 생성하는 클래스"""
    
    def __init__(self):
        self.weights = config.INDICATOR_WEIGHTS
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        기술적 지표를 계산합니다.
        
        Args:
            data: OHLCV 데이터
        
        Returns:
            지표가 추가된 DataFrame
        """
        df = data.copy()
        
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=config.RSI_PERIOD).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['close'], 
                            window_fast=config.MACD_FAST,
                            window_slow=config.MACD_SLOW,
                            window_sign=config.MACD_SIGNAL)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # 이동평균선
        df['ma_short'] = df['close'].rolling(window=config.MA_SHORT).mean()
        df['ma_long'] = df['close'].rolling(window=config.MA_LONG).mean()
        
        # 볼린저 밴드
        bb = ta.volatility.BollingerBands(df['close'], 
                                         window=config.BB_PERIOD,
                                         window_dev=config.BB_STD)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_middle'] = bb.bollinger_mavg()
        
        # 거래량 이동평균
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        
        # 모멘텀 (가격 변화율)
        df['momentum'] = df['close'].pct_change(periods=10) * 100
        
        return df
    
    def score_rsi(self, rsi: float) -> float:
        """RSI 점수를 계산합니다 (0-1)."""
        if pd.isna(rsi):
            return 0.5
        
        # RSI가 30-50 사이면 매수 신호 (과매도 구간)
        if 30 <= rsi < 50:
            return 1.0 - (rsi - 30) / 20  # 30에서 1.0, 50에서 0.5
        elif rsi < 30:
            return 1.0  # 강한 과매도
        elif 50 <= rsi < 70:
            return 0.5 - (rsi - 50) / 40  # 50에서 0.5, 70에서 0.0
        else:
            return 0.0  # 과매수
    
    def score_macd(self, macd: float, signal: float, diff: float) -> float:
        """MACD 점수를 계산합니다 (0-1)."""
        if pd.isna(macd) or pd.isna(signal) or pd.isna(diff):
            return 0.5
        
        score = 0.5
        
        # MACD가 시그널을 상향 돌파하면 매수 신호
        if macd > signal:
            score += 0.3
        
        # MACD 차이가 양수이고 증가 추세면 추가 점수
        if diff > 0:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def score_moving_average(self, price: float, ma_short: float, ma_long: float) -> float:
        """이동평균선 점수를 계산합니다 (0-1)."""
        if pd.isna(price) or pd.isna(ma_short) or pd.isna(ma_long):
            return 0.5
        
        score = 0.5
        
        # 단기 이동평균이 장기 이동평균 위에 있으면 골든크로스
        if ma_short > ma_long:
            score += 0.3
        
        # 현재 가격이 단기 이동평균 위에 있으면 추가 점수
        if price > ma_short:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def score_bollinger_bands(self, price: float, bb_lower: float, bb_upper: float, bb_middle: float) -> float:
        """볼린저 밴드 점수를 계산합니다 (0-1)."""
        if pd.isna(price) or pd.isna(bb_lower) or pd.isna(bb_upper):
            return 0.5
        
        # 가격이 하단 밴드 근처에 있으면 매수 신호
        band_width = bb_upper - bb_lower
        if band_width == 0:
            return 0.5
        
        distance_from_lower = (price - bb_lower) / band_width
        
        if distance_from_lower < 0.2:  # 하단 밴드 근처
            return 1.0
        elif distance_from_lower < 0.4:
            return 0.8
        elif distance_from_lower < 0.6:
            return 0.5
        else:
            return 0.3
    
    def score_volume(self, volume: float, volume_ma: float) -> float:
        """거래량 점수를 계산합니다 (0-1)."""
        if pd.isna(volume) or pd.isna(volume_ma) or volume_ma == 0:
            return 0.5
        
        # 거래량이 평균보다 높으면 매수 신호 (관심 증가)
        volume_ratio = volume / volume_ma
        
        if volume_ratio > 1.5:
            return 1.0
        elif volume_ratio > 1.2:
            return 0.8
        elif volume_ratio > 1.0:
            return 0.6
        else:
            return 0.4
    
    def score_momentum(self, momentum: float) -> float:
        """모멘텀 점수를 계산합니다 (0-1)."""
        if pd.isna(momentum):
            return 0.5
        
        # 양의 모멘텀이 있지만 과도하지 않으면 매수 신호
        if 0 < momentum < 5:  # 적당한 상승 모멘텀
            return 1.0
        elif -2 < momentum <= 0:  # 약한 하락 또는 횡보
            return 0.7
        elif momentum > 5:  # 과도한 상승 (조정 가능)
            return 0.4
        else:  # 강한 하락
            return 0.2
    
    def calculate_signal_score(self, row: pd.Series) -> float:
        """
        종합 점수를 계산합니다 (0-10).
        
        Args:
            row: 기술적 지표가 포함된 데이터 행
        
        Returns:
            0-10 사이의 점수
        """
        scores = {}
        
        # 각 지표별 점수 계산
        scores['rsi'] = self.score_rsi(row.get('rsi', np.nan))
        scores['macd'] = self.score_macd(
            row.get('macd', np.nan),
            row.get('macd_signal', np.nan),
            row.get('macd_diff', np.nan)
        )
        scores['moving_average'] = self.score_moving_average(
            row.get('close', np.nan),
            row.get('ma_short', np.nan),
            row.get('ma_long', np.nan)
        )
        scores['bollinger_bands'] = self.score_bollinger_bands(
            row.get('close', np.nan),
            row.get('bb_lower', np.nan),
            row.get('bb_upper', np.nan),
            row.get('bb_middle', np.nan)
        )
        scores['volume'] = self.score_volume(
            row.get('volume', np.nan),
            row.get('volume_ma', np.nan)
        )
        scores['momentum'] = self.score_momentum(row.get('momentum', np.nan))
        
        # 가중 평균 계산
        total_score = 0
        total_weight = 0
        
        for indicator, weight in self.weights.items():
            if indicator in scores:
                total_score += scores[indicator] * weight
                total_weight += weight
        
        if total_weight > 0:
            normalized_score = (total_score / total_weight) * 10
        else:
            normalized_score = 5.0
        
        return round(normalized_score, 2)
    
    def get_signal_level(self, score: float) -> str:
        """
        점수에 따라 신호 레벨을 반환합니다.
        
        Args:
            score: 0-10 사이의 점수
        
        Returns:
            신호 레벨 (STRONG_BUY, BUY, WATCH, 또는 HOLD)
        """
        if score >= 8:
            return 'STRONG_BUY'
        elif score >= 5:
            return 'BUY'
        elif score >= 3:
            return 'WATCH'
        else:
            return 'HOLD'
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        매수 신호를 생성합니다.
        
        Args:
            data: OHLCV 데이터
        
        Returns:
            신호가 추가된 DataFrame
        """
        df = self.calculate_technical_indicators(data)
        
        # 각 행에 대해 점수 계산
        scores = []
        signal_levels = []
        
        for idx, row in df.iterrows():
            score = self.calculate_signal_score(row)
            level = self.get_signal_level(score)
            
            scores.append(score)
            signal_levels.append(level)
        
        df['signal_score'] = scores
        df['signal_level'] = signal_levels
        
        return df
    
    def get_current_signals(self, data: pd.DataFrame) -> Dict:
        """
        현재 시점의 매수 신호를 반환합니다.
        
        Args:
            data: OHLCV 데이터
        
        Returns:
            현재 신호 정보 딕셔너리
        """
        df = self.generate_signals(data)
        
        if df.empty:
            return None
        
        latest = df.iloc[-1]
        
        return {
            'symbol': data.attrs.get('symbol', 'UNKNOWN') if hasattr(data, 'attrs') else 'UNKNOWN',
            'date': latest.name,
            'price': latest['close'],
            'score': latest['signal_score'],
            'level': latest['signal_level'],
            'rsi': latest.get('rsi', np.nan),
            'macd': latest.get('macd', np.nan),
            'ma_short': latest.get('ma_short', np.nan),
            'ma_long': latest.get('ma_long', np.nan),
        }

