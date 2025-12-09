"""유명 투자자 방법론 기반 점수 계산"""
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

def get_financial_data(symbol):
    """yfinance를 통해 재무 지표 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'trailingPE': info.get('trailingPE'),
            'forwardPE': info.get('forwardPE'),
            'priceToBook': info.get('priceToBook'),
            'returnOnEquity': info.get('returnOnEquity'),
            'debtToEquity': info.get('debtToEquity'),
            'revenueGrowth': info.get('revenueGrowth'),
            'earningsGrowth': info.get('earningsGrowth'),
            'profitMargins': info.get('profitMargins'),
            'marketCap': info.get('marketCap', 0),
            'dividendYield': info.get('dividendYield'),
            'currentRatio': info.get('currentRatio'),
            'quickRatio': info.get('quickRatio'),
            'pegRatio': info.get('pegRatio'),
            'enterpriseToRevenue': info.get('enterpriseToRevenue'),
            'enterpriseToEbitda': info.get('enterpriseToEbitda'),
            '52WeekHigh': info.get('fiftyTwoWeekHigh'),
            '52WeekLow': info.get('fiftyTwoWeekLow'),
            'currentPrice': info.get('currentPrice', info.get('regularMarketPrice', 0))
        }
    except:
        return None

def calculate_value_score(symbol, price_data):
    """
    유명 투자자 방법론 기반 종합 점수 계산 (0-10점)
    
    포함된 방법론:
    1. 워렌 버핏 (Warren Buffett) - 가치투자, ROE, 부채비율
    2. 피터 린치 (Peter Lynch) - 성장주, PEG 비율
    3. 벤저민 그레이엄 (Benjamin Graham) - 안전마진, PER, PBR
    4. 조지 소로스 (George Soros) - 추세 추종
    5. 존 네프 (John Neff) - 저PER 투자
    """
    if price_data is None or price_data.empty or len(price_data) < 20:
        return 0.0, {}
    
    try:
        score = 0.0
        reasons = {}
        max_score = 0.0
        
        # 재무 지표 가져오기
        financial = get_financial_data(symbol)
        if financial is None:
            return 0.0, {'error': '재무 데이터 없음'}
        
        current_price = financial.get('currentPrice', 0)
        if current_price == 0:
            current_price = price_data['Close'].iloc[-1]
        
        # ============================================
        # 1. 워렌 버핏 (Warren Buffett) - 가치투자
        # ============================================
        # ROE (자기자본이익률) - 15% 이상 우수
        roe = financial.get('returnOnEquity')
        if roe is not None and roe > 0:
            max_score += 2.0
            if roe >= 20:
                score += 2.0
                reasons['buffett_roe'] = f"ROE {roe:.1f}% (우수)"
            elif roe >= 15:
                score += 1.5
                reasons['buffett_roe'] = f"ROE {roe:.1f}% (양호)"
            elif roe >= 10:
                score += 1.0
                reasons['buffett_roe'] = f"ROE {roe:.1f}% (보통)"
            else:
                reasons['buffett_roe'] = f"ROE {roe:.1f}% (낮음)"
        
        # 부채비율 (Debt to Equity) - 낮을수록 좋음
        debt_to_equity = financial.get('debtToEquity')
        if debt_to_equity is not None and debt_to_equity >= 0:
            max_score += 1.0
            if debt_to_equity <= 30:
                score += 1.0
                reasons['buffett_debt'] = f"부채비율 {debt_to_equity:.1f}% (우수)"
            elif debt_to_equity <= 50:
                score += 0.7
                reasons['buffett_debt'] = f"부채비율 {debt_to_equity:.1f}% (양호)"
            elif debt_to_equity <= 100:
                score += 0.3
                reasons['buffett_debt'] = f"부채비율 {debt_to_equity:.1f}% (보통)"
            else:
                reasons['buffett_debt'] = f"부채비율 {debt_to_equity:.1f}% (높음)"
        
        # ============================================
        # 2. 벤저민 그레이엄 (Benjamin Graham) - 안전마진
        # ============================================
        # PER (주가수익비율) - 낮을수록 좋음
        trailing_pe = financial.get('trailingPE')
        if trailing_pe is not None and trailing_pe > 0:
            max_score += 1.5
            if trailing_pe <= 15:
                score += 1.5
                reasons['graham_pe'] = f"PER {trailing_pe:.1f} (저평가)"
            elif trailing_pe <= 20:
                score += 1.0
                reasons['graham_pe'] = f"PER {trailing_pe:.1f} (적정)"
            elif trailing_pe <= 25:
                score += 0.5
                reasons['graham_pe'] = f"PER {trailing_pe:.1f} (다소 고평가)"
            else:
                reasons['graham_pe'] = f"PER {trailing_pe:.1f} (고평가)"
        
        # PBR (주가순자산비율) - 1.5 이하 선호
        pbr = financial.get('priceToBook')
        if pbr is not None and pbr > 0:
            max_score += 1.0
            if pbr <= 1.0:
                score += 1.0
                reasons['graham_pbr'] = f"PBR {pbr:.2f} (매우 저평가)"
            elif pbr <= 1.5:
                score += 0.8
                reasons['graham_pbr'] = f"PBR {pbr:.2f} (저평가)"
            elif pbr <= 2.5:
                score += 0.5
                reasons['graham_pbr'] = f"PBR {pbr:.2f} (적정)"
            else:
                reasons['graham_pbr'] = f"PBR {pbr:.2f} (고평가)"
        
        # 유동비율 (Current Ratio) - 2.0 이상 선호
        current_ratio = financial.get('currentRatio')
        if current_ratio is not None and current_ratio > 0:
            max_score += 0.5
            if current_ratio >= 2.0:
                score += 0.5
                reasons['graham_liquidity'] = f"유동비율 {current_ratio:.2f} (우수)"
            elif current_ratio >= 1.5:
                score += 0.3
                reasons['graham_liquidity'] = f"유동비율 {current_ratio:.2f} (양호)"
            else:
                reasons['graham_liquidity'] = f"유동비율 {current_ratio:.2f} (낮음)"
        
        # ============================================
        # 3. 피터 린치 (Peter Lynch) - 성장주 투자
        # ============================================
        # PEG 비율 (PER / 성장률) - 1.0 이하 선호
        peg = financial.get('pegRatio')
        if peg is not None and peg > 0:
            max_score += 1.5
            if peg <= 0.5:
                score += 1.5
                reasons['lynch_peg'] = f"PEG {peg:.2f} (매우 우수)"
            elif peg <= 1.0:
                score += 1.2
                reasons['lynch_peg'] = f"PEG {peg:.2f} (우수)"
            elif peg <= 1.5:
                score += 0.8
                reasons['lynch_peg'] = f"PEG {peg:.2f} (양호)"
            elif peg <= 2.0:
                score += 0.4
                reasons['lynch_peg'] = f"PEG {peg:.2f} (보통)"
            else:
                reasons['lynch_peg'] = f"PEG {peg:.2f} (높음)"
        
        # 매출 성장률 (Revenue Growth)
        revenue_growth = financial.get('revenueGrowth')
        if revenue_growth is not None:
            max_score += 1.0
            if revenue_growth >= 0.20:  # 20% 이상
                score += 1.0
                reasons['lynch_revenue'] = f"매출 성장률 {revenue_growth*100:.1f}% (우수)"
            elif revenue_growth >= 0.10:  # 10% 이상
                score += 0.7
                reasons['lynch_revenue'] = f"매출 성장률 {revenue_growth*100:.1f}% (양호)"
            elif revenue_growth >= 0.05:  # 5% 이상
                score += 0.4
                reasons['lynch_revenue'] = f"매출 성장률 {revenue_growth*100:.1f}% (보통)"
            elif revenue_growth < 0:
                reasons['lynch_revenue'] = f"매출 성장률 {revenue_growth*100:.1f}% (감소)"
        
        # 이익 성장률 (Earnings Growth)
        earnings_growth = financial.get('earningsGrowth')
        if earnings_growth is not None:
            max_score += 0.5
            if earnings_growth >= 0.20:  # 20% 이상
                score += 0.5
                reasons['lynch_earnings'] = f"이익 성장률 {earnings_growth*100:.1f}% (우수)"
            elif earnings_growth >= 0.10:  # 10% 이상
                score += 0.3
                reasons['lynch_earnings'] = f"이익 성장률 {earnings_growth*100:.1f}% (양호)"
            elif earnings_growth < 0:
                reasons['lynch_earnings'] = f"이익 성장률 {earnings_growth*100:.1f}% (감소)"
        
        # ============================================
        # 4. 조지 소로스 (George Soros) - 추세 추종
        # ============================================
        # 52주 고점 대비 현재가 위치
        week_52_high = financial.get('52WeekHigh')
        week_52_low = financial.get('52WeekLow')
        if week_52_high and week_52_low and week_52_high > week_52_low:
            max_score += 0.5
            price_position = (current_price - week_52_low) / (week_52_high - week_52_low)
            # 52주 고점 근처에 있으면 추세 상승 중
            if price_position >= 0.8:
                score += 0.5
                reasons['soros_trend'] = f"52주 고점 근처 ({price_position*100:.0f}%)"
            elif price_position >= 0.6:
                score += 0.3
                reasons['soros_trend'] = f"52주 중상단 ({price_position*100:.0f}%)"
            elif price_position <= 0.2:
                reasons['soros_trend'] = f"52주 저점 근처 ({price_position*100:.0f}%)"
        
        # 가격 추세 (최근 6개월)
        if len(price_data) >= 60:
            price_6mo_ago = price_data['Close'].iloc[-60]
            price_trend = (current_price - price_6mo_ago) / price_6mo_ago
            max_score += 0.5
            if price_trend >= 0.20:  # 20% 이상 상승
                score += 0.5
                reasons['soros_momentum'] = f"6개월 상승률 {price_trend*100:.1f}%"
            elif price_trend >= 0.10:  # 10% 이상 상승
                score += 0.3
                reasons['soros_momentum'] = f"6개월 상승률 {price_trend*100:.1f}%"
            elif price_trend < -0.20:  # 20% 이상 하락
                reasons['soros_momentum'] = f"6개월 하락률 {price_trend*100:.1f}%"
        
        # ============================================
        # 5. 존 네프 (John Neff) - 저PER + 배당
        # ============================================
        # 배당 수익률
        dividend_yield = financial.get('dividendYield')
        if dividend_yield is not None and dividend_yield > 0:
            max_score += 0.5
            if dividend_yield >= 0.04:  # 4% 이상
                score += 0.5
                reasons['neff_dividend'] = f"배당 수익률 {dividend_yield*100:.2f}% (우수)"
            elif dividend_yield >= 0.02:  # 2% 이상
                score += 0.3
                reasons['neff_dividend'] = f"배당 수익률 {dividend_yield*100:.2f}% (양호)"
            else:
                reasons['neff_dividend'] = f"배당 수익률 {dividend_yield*100:.2f}% (낮음)"
        
        # ============================================
        # 6. 추가 지표
        # ============================================
        # 순이익률 (Profit Margin)
        profit_margin = financial.get('profitMargins')
        if profit_margin is not None and profit_margin > 0:
            max_score += 0.5
            if profit_margin >= 0.20:  # 20% 이상
                score += 0.5
                reasons['profit_margin'] = f"순이익률 {profit_margin*100:.1f}% (우수)"
            elif profit_margin >= 0.10:  # 10% 이상
                score += 0.3
                reasons['profit_margin'] = f"순이익률 {profit_margin*100:.1f}% (양호)"
            else:
                reasons['profit_margin'] = f"순이익률 {profit_margin*100:.1f}% (낮음)"
        
        # 최대 10점으로 정규화
        if max_score > 0:
            normalized_score = (score / max_score) * 10.0
        else:
            normalized_score = 0.0
        
        return min(normalized_score, 10.0), reasons
        
    except Exception as e:
        return 0.0, {'error': str(e)}

def generate_value_signal(symbol, price_data):
    """가치투자 방법론 기반 매수 신호 생성"""
    if price_data is None or price_data.empty:
        return None
    
    try:
        score, reasons = calculate_value_score(symbol, price_data)
        
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
                'method': 'value_investing'
            }
        
        return None
    except Exception as e:
        return None

