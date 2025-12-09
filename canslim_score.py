"""윌리엄 오닐(William O'Neil) CAN SLIM 방법론 기반 점수 계산"""
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

def get_canslim_data(symbol):
    """CAN SLIM 분석에 필요한 데이터 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        financials = ticker.financials
        quarterly_earnings = ticker.quarterly_financials
        
        return {
            'info': info,
            'financials': financials,
            'quarterly_earnings': quarterly_earnings,
            'currentPrice': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'marketCap': info.get('marketCap', 0),
            'volume': info.get('volume', 0),
            'averageVolume': info.get('averageVolume', 0),
            '52WeekHigh': info.get('fiftyTwoWeekHigh', 0),
            '52WeekLow': info.get('fiftyTwoWeekLow', 0),
            'sharesOutstanding': info.get('sharesOutstanding', 0),
            'institutionalOwnership': info.get('heldPercentInstitutions', 0),
            'earningsQuarterlyGrowth': info.get('earningsQuarterlyGrowth'),
            'earningsGrowth': info.get('earningsGrowth'),
            'revenueGrowth': info.get('revenueGrowth'),
            'returnOnEquity': info.get('returnOnEquity'),
            'profitMargins': info.get('profitMargins')
        }
    except:
        return None

def calculate_canslim_score(symbol, price_data):
    """
    윌리엄 오닐 CAN SLIM 방법론 기반 점수 계산 (0-10점)
    
    CAN SLIM:
    C - Current quarterly earnings (분기 실적)
    A - Annual earnings growth (연간 이익 성장)
    N - New products, new management, new highs (신제품, 신경영진, 신고가)
    S - Supply and demand (공급과 수요)
    L - Leader or laggard (선도주 또는 후행주)
    I - Institutional sponsorship (기관 투자자 지지)
    M - Market direction (시장 방향)
    """
    if price_data is None or price_data.empty or len(price_data) < 20:
        return 0.0, {}
    
    try:
        score = 0.0
        reasons = {}
        max_score = 0.0
        
        # CAN SLIM 데이터 가져오기
        canslim_data = get_canslim_data(symbol)
        if canslim_data is None:
            return 0.0, {'error': 'CAN SLIM 데이터 없음'}
        
        current_price = canslim_data.get('currentPrice', 0)
        if current_price == 0:
            current_price = price_data['Close'].iloc[-1]
        
        # ============================================
        # C - Current Quarterly Earnings (분기 실적)
        # ============================================
        # 분기 이익 성장률 25% 이상 선호
        earnings_q_growth = canslim_data.get('earningsQuarterlyGrowth')
        if earnings_q_growth is not None:
            max_score += 2.0
            if earnings_q_growth >= 0.50:  # 50% 이상
                score += 2.0
                reasons['C_earnings'] = f"분기 이익 성장 {earnings_q_growth*100:.0f}% (매우 우수)"
            elif earnings_q_growth >= 0.25:  # 25% 이상
                score += 1.5
                reasons['C_earnings'] = f"분기 이익 성장 {earnings_q_growth*100:.0f}% (우수)"
            elif earnings_q_growth >= 0.10:  # 10% 이상
                score += 1.0
                reasons['C_earnings'] = f"분기 이익 성장 {earnings_q_growth*100:.0f}% (양호)"
            elif earnings_q_growth >= 0:
                score += 0.5
                reasons['C_earnings'] = f"분기 이익 성장 {earnings_q_growth*100:.0f}% (보통)"
            else:
                reasons['C_earnings'] = f"분기 이익 감소 {earnings_q_growth*100:.0f}% (불량)"
        
        # ============================================
        # A - Annual Earnings Growth (연간 이익 성장)
        # ============================================
        # 연간 이익 성장률 25% 이상 선호
        earnings_growth = canslim_data.get('earningsGrowth')
        if earnings_growth is not None:
            max_score += 2.0
            if earnings_growth >= 0.50:  # 50% 이상
                score += 2.0
                reasons['A_annual'] = f"연간 이익 성장 {earnings_growth*100:.0f}% (매우 우수)"
            elif earnings_growth >= 0.25:  # 25% 이상
                score += 1.5
                reasons['A_annual'] = f"연간 이익 성장 {earnings_growth*100:.0f}% (우수)"
            elif earnings_growth >= 0.10:  # 10% 이상
                score += 1.0
                reasons['A_annual'] = f"연간 이익 성장 {earnings_growth*100:.0f}% (양호)"
            elif earnings_growth >= 0:
                score += 0.5
                reasons['A_annual'] = f"연간 이익 성장 {earnings_growth*100:.0f}% (보통)"
            else:
                reasons['A_annual'] = f"연간 이익 감소 {earnings_growth*100:.0f}% (불량)"
        
        # ============================================
        # N - New Highs (신고가)
        # ============================================
        # 52주 고점 근처 또는 신고가 돌파
        week_52_high = canslim_data.get('52WeekHigh', 0)
        week_52_low = canslim_data.get('52WeekLow', 0)
        if week_52_high > 0 and week_52_low > 0:
            max_score += 1.5
            price_position = (current_price - week_52_low) / (week_52_high - week_52_low)
            
            # 52주 고점의 95% 이상이면 신고가 근처
            if current_price >= week_52_high * 0.95:
                score += 1.5
                reasons['N_newhigh'] = f"52주 고점 근처 ({current_price/week_52_high*100:.1f}%)"
            elif price_position >= 0.85:
                score += 1.2
                reasons['N_newhigh'] = f"52주 상단권 ({price_position*100:.0f}%)"
            elif price_position >= 0.70:
                score += 0.8
                reasons['N_newhigh'] = f"52주 중상단 ({price_position*100:.0f}%)"
            elif price_position >= 0.50:
                score += 0.4
                reasons['N_newhigh'] = f"52주 중단 ({price_position*100:.0f}%)"
            else:
                reasons['N_newhigh'] = f"52주 하단 ({price_position*100:.0f}%)"
        
        # 최근 3개월 신고가 돌파 여부
        if len(price_data) >= 60:
            recent_high = price_data['High'].tail(60).max()
            if current_price >= recent_high * 0.98:  # 최근 고점의 98% 이상
                max_score += 0.5
                score += 0.5
                reasons['N_recent_high'] = "최근 3개월 고점 근처"
        
        # ============================================
        # S - Supply and Demand (공급과 수요)
        # ============================================
        # 거래량 증가 (평균 대비 50% 이상 증가 선호)
        avg_volume = canslim_data.get('averageVolume', 0)
        current_volume = canslim_data.get('volume', 0)
        if avg_volume > 0 and current_volume > 0:
            max_score += 1.5
            volume_ratio = current_volume / avg_volume
            if volume_ratio >= 2.0:  # 평균의 2배 이상
                score += 1.5
                reasons['S_volume'] = f"거래량 {volume_ratio:.1f}배 (매우 활발)"
            elif volume_ratio >= 1.5:  # 평균의 1.5배 이상
                score += 1.2
                reasons['S_volume'] = f"거래량 {volume_ratio:.1f}배 (활발)"
            elif volume_ratio >= 1.2:  # 평균의 1.2배 이상
                score += 0.8
                reasons['S_volume'] = f"거래량 {volume_ratio:.1f}배 (증가)"
            elif volume_ratio >= 1.0:
                score += 0.4
                reasons['S_volume'] = f"거래량 {volume_ratio:.1f}배 (보통)"
            else:
                reasons['S_volume'] = f"거래량 {volume_ratio:.1f}배 (감소)"
        
        # 가격 데이터의 최근 거래량 분석
        if len(price_data) >= 20:
            recent_volume = price_data['Volume'].tail(5).mean()
            avg_volume_20 = price_data['Volume'].tail(20).mean()
            if avg_volume_20 > 0:
                volume_trend = recent_volume / avg_volume_20
                max_score += 0.5
                if volume_trend >= 1.5:
                    score += 0.5
                    reasons['S_volume_trend'] = f"최근 거래량 증가 추세 ({volume_trend:.1f}배)"
                elif volume_trend >= 1.2:
                    score += 0.3
                    reasons['S_volume_trend'] = f"최근 거래량 증가 ({volume_trend:.1f}배)"
        
        # ============================================
        # L - Leader or Laggard (선도주 또는 후행주)
        # ============================================
        # 상대 강도 (RS Rating) - 최근 6개월 수익률
        if len(price_data) >= 120:
            price_6mo_ago = price_data['Close'].iloc[-120]
            price_6mo_return = (current_price - price_6mo_ago) / price_6mo_ago
            max_score += 1.5
            if price_6mo_return >= 0.30:  # 30% 이상 상승
                score += 1.5
                reasons['L_leader'] = f"6개월 수익률 {price_6mo_return*100:.1f}% (선도주)"
            elif price_6mo_return >= 0.20:  # 20% 이상 상승
                score += 1.2
                reasons['L_leader'] = f"6개월 수익률 {price_6mo_return*100:.1f}% (강세)"
            elif price_6mo_return >= 0.10:  # 10% 이상 상승
                score += 0.8
                reasons['L_leader'] = f"6개월 수익률 {price_6mo_return*100:.1f}% (양호)"
            elif price_6mo_return >= 0:
                score += 0.4
                reasons['L_leader'] = f"6개월 수익률 {price_6mo_return*100:.1f}% (보통)"
            else:
                reasons['L_leader'] = f"6개월 수익률 {price_6mo_return*100:.1f}% (후행주)"
        
        # ROE (자기자본이익률) - 17% 이상 선호
        roe = canslim_data.get('returnOnEquity')
        if roe is not None and roe > 0:
            max_score += 0.5
            if roe >= 25:
                score += 0.5
                reasons['L_roe'] = f"ROE {roe:.1f}% (우수)"
            elif roe >= 17:
                score += 0.3
                reasons['L_roe'] = f"ROE {roe:.1f}% (양호)"
            else:
                reasons['L_roe'] = f"ROE {roe:.1f}% (낮음)"
        
        # ============================================
        # I - Institutional Sponsorship (기관 투자자 지지)
        # ============================================
        # 기관 투자자 보유 비율
        inst_ownership = canslim_data.get('institutionalOwnership')
        if inst_ownership is not None:
            max_score += 1.0
            if inst_ownership >= 0.60:  # 60% 이상
                score += 1.0
                reasons['I_institutional'] = f"기관 보유율 {inst_ownership*100:.1f}% (높음)"
            elif inst_ownership >= 0.40:  # 40% 이상
                score += 0.7
                reasons['I_institutional'] = f"기관 보유율 {inst_ownership*100:.1f}% (양호)"
            elif inst_ownership >= 0.20:  # 20% 이상
                score += 0.4
                reasons['I_institutional'] = f"기관 보유율 {inst_ownership*100:.1f}% (보통)"
            else:
                reasons['I_institutional'] = f"기관 보유율 {inst_ownership*100:.1f}% (낮음)"
        
        # 최근 기관 매수 여부 (거래량과 가격 상승으로 추정)
        if len(price_data) >= 20:
            recent_price_change = (price_data['Close'].iloc[-1] - price_data['Close'].iloc[-20]) / price_data['Close'].iloc[-20]
            recent_volume_avg = price_data['Volume'].tail(5).mean()
            prev_volume_avg = price_data['Volume'].iloc[-20:-10].mean()
            if recent_volume_avg > 0 and prev_volume_avg > 0:
                volume_increase = recent_volume_avg / prev_volume_avg
                if recent_price_change > 0.05 and volume_increase > 1.3:  # 가격 상승 + 거래량 증가
                    max_score += 0.5
                    score += 0.5
                    reasons['I_buying'] = "기관 매수 추정 (가격↑ + 거래량↑)"
        
        # ============================================
        # M - Market Direction (시장 방향)
        # ============================================
        # 시장 전체 방향은 개별 종목 분석에서는 제외
        # (시장 지수 분석이 필요하므로 여기서는 스킵)
        # 대신 종목의 시장 대비 상대 강도로 대체
        max_score += 0.5
        score += 0.5  # 기본 점수 (시장 방향은 별도 분석 필요)
        reasons['M_market'] = "시장 방향 (별도 분석 필요)"
        
        # ============================================
        # 추가 지표
        # ============================================
        # 매출 성장률
        revenue_growth = canslim_data.get('revenueGrowth')
        if revenue_growth is not None:
            max_score += 0.5
            if revenue_growth >= 0.25:  # 25% 이상
                score += 0.5
                reasons['revenue_growth'] = f"매출 성장률 {revenue_growth*100:.1f}% (우수)"
            elif revenue_growth >= 0.15:  # 15% 이상
                score += 0.3
                reasons['revenue_growth'] = f"매출 성장률 {revenue_growth*100:.1f}% (양호)"
            elif revenue_growth >= 0:
                score += 0.1
                reasons['revenue_growth'] = f"매출 성장률 {revenue_growth*100:.1f}% (보통)"
        
        # 순이익률
        profit_margin = canslim_data.get('profitMargins')
        if profit_margin is not None and profit_margin > 0:
            max_score += 0.5
            if profit_margin >= 0.20:  # 20% 이상
                score += 0.5
                reasons['profit_margin'] = f"순이익률 {profit_margin*100:.1f}% (우수)"
            elif profit_margin >= 0.10:  # 10% 이상
                score += 0.3
                reasons['profit_margin'] = f"순이익률 {profit_margin*100:.1f}% (양호)"
        
        # 최대 10점으로 정규화
        if max_score > 0:
            normalized_score = (score / max_score) * 10.0
        else:
            normalized_score = 0.0
        
        return min(normalized_score, 10.0), reasons
        
    except Exception as e:
        return 0.0, {'error': str(e)}

def generate_canslim_signal(symbol, price_data):
    """CAN SLIM 방법론 기반 매수 신호 생성"""
    if price_data is None or price_data.empty:
        return None
    
    try:
        score, reasons = calculate_canslim_score(symbol, price_data)
        
        # 7.5점 이상만 신호 반환
        if score >= 7.5:
            current_price = price_data['Close'].iloc[-1]
            return {
                'symbol': symbol,
                'level': 'BUY',
                'score': round(score, 2),
                'price': round(current_price, 2),
                'date': datetime.now().isoformat(),
                'reasons': reasons,
                'method': 'canslim'
            }
        
        return None
    except Exception as e:
        return None

