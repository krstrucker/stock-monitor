"""
백테스팅 엔진
과거 데이터로 매수 신호의 수익률을 검증합니다.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from signal_generator import SignalGenerator
import config


class Backtester:
    """백테스팅을 수행하는 클래스"""
    
    def __init__(self, initial_capital: float = 100000):
        """
        Args:
            initial_capital: 초기 자본금
        """
        self.initial_capital = initial_capital
        self.signal_generator = SignalGenerator()
    
    def backtest_strategy(self, 
                         data: pd.DataFrame,
                         signal_level: str = 'BUY',
                         min_score: float = 5.0,
                         hold_days: int = 5,
                         stop_loss: float = 0.05,
                         take_profit: float = 0.10) -> Dict:
        """
        백테스팅을 수행합니다.
        
        Args:
            data: OHLCV 데이터
            signal_level: 매수 신호 레벨 (STRONG_BUY, BUY, WATCH)
            min_score: 최소 점수
            hold_days: 보유 기간 (일)
            stop_loss: 손절매 비율 (5% = 0.05)
            take_profit: 익절매 비율 (10% = 0.10)
        
        Returns:
            백테스팅 결과 딕셔너리
        """
        df = self.signal_generator.generate_signals(data)
        
        if df.empty:
            return None
        
        capital = self.initial_capital
        positions = []  # [(entry_date, entry_price, shares, exit_date, exit_price, pnl)]
        current_position = None
        
        for i in range(len(df)):
            row = df.iloc[i]
            current_date = row.name
            current_price = row['close']
            signal_score = row['signal_score']
            signal_level_current = row['signal_level']
            
            # 포지션이 없을 때
            if current_position is None:
                # 매수 신호 확인
                if signal_level_current == signal_level and signal_score >= min_score:
                    # 매수 실행
                    shares = int(capital / current_price)
                    if shares > 0:
                        cost = shares * current_price
                        capital -= cost
                        current_position = {
                            'entry_date': current_date,
                            'entry_price': current_price,
                            'shares': shares,
                            'signal_score': signal_score
                        }
            
            # 포지션이 있을 때
            else:
                entry_price = current_position['entry_price']
                shares = current_position['shares']
                entry_date = current_position['entry_date']
                
                # 수익률 계산
                pnl_ratio = (current_price - entry_price) / entry_price
                pnl = (current_price - entry_price) * shares
                
                # 보유 기간 계산
                days_held = (current_date - entry_date).days if hasattr(current_date - entry_date, 'days') else 0
                
                # 익절 또는 손절 확인
                should_exit = False
                exit_reason = ""
                
                if pnl_ratio >= take_profit:
                    should_exit = True
                    exit_reason = "익절"
                elif pnl_ratio <= -stop_loss:
                    should_exit = True
                    exit_reason = "손절"
                elif days_held >= hold_days:
                    should_exit = True
                    exit_reason = "보유기간 종료"
                
                # 매도 실행
                if should_exit:
                    capital += shares * current_price
                    positions.append({
                        'entry_date': entry_date,
                        'entry_price': entry_price,
                        'exit_date': current_date,
                        'exit_price': current_price,
                        'shares': shares,
                        'pnl': pnl,
                        'pnl_ratio': pnl_ratio * 100,
                        'days_held': days_held,
                        'exit_reason': exit_reason,
                        'signal_score': current_position['signal_score']
                    })
                    current_position = None
        
        # 마지막 포지션이 있으면 청산
        if current_position is not None:
            last_row = df.iloc[-1]
            last_price = last_row['close']
            last_date = last_row.name
            shares = current_position['shares']
            entry_price = current_position['entry_price']
            entry_date = current_position['entry_date']
            
            pnl = (last_price - entry_price) * shares
            pnl_ratio = (last_price - entry_price) / entry_price
            days_held = (last_date - entry_date).days if hasattr(last_date - entry_date, 'days') else 0
            
            capital += shares * last_price
            positions.append({
                'entry_date': entry_date,
                'entry_price': entry_price,
                'exit_date': last_date,
                'exit_price': last_price,
                'shares': shares,
                'pnl': pnl,
                'pnl_ratio': pnl_ratio * 100,
                'days_held': days_held,
                'exit_reason': "백테스트 종료",
                'signal_score': current_position['signal_score']
            })
        
        # 결과 계산
        total_trades = len(positions)
        if total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'final_capital': capital,
                'positions': []
            }
        
        winning_trades = [p for p in positions if p['pnl'] > 0]
        losing_trades = [p for p in positions if p['pnl'] <= 0]
        
        win_rate = len(winning_trades) / total_trades * 100
        total_pnl = sum(p['pnl'] for p in positions)
        total_return = (capital - self.initial_capital) / self.initial_capital * 100
        
        avg_win = np.mean([p['pnl'] for p in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([p['pnl'] for p in losing_trades]) if losing_trades else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'total_return': round(total_return, 2),
            'final_capital': round(capital, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
            'positions': positions
        }
    
    def compare_strategies(self, 
                          data: pd.DataFrame,
                          hold_days_list: List[int] = [1, 3, 5, 10, 20],
                          stop_loss: float = 0.05,
                          take_profit: float = 0.10) -> pd.DataFrame:
        """
        다양한 전략을 비교합니다.
        
        Args:
            data: OHLCV 데이터
            hold_days_list: 테스트할 보유 기간 리스트
            stop_loss: 손절매 비율
            take_profit: 익절매 비율
        
        Returns:
            전략 비교 결과 DataFrame
        """
        results = []
        
        for signal_level in ['STRONG_BUY', 'BUY', 'WATCH']:
            min_score = {
                'STRONG_BUY': 8.0,
                'BUY': 5.0,
                'WATCH': 3.0
            }[signal_level]
            
            for hold_days in hold_days_list:
                result = self.backtest_strategy(
                    data,
                    signal_level=signal_level,
                    min_score=min_score,
                    hold_days=hold_days,
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
                
                if result and result['total_trades'] > 0:
                    results.append({
                        'signal_level': signal_level,
                        'hold_days': hold_days,
                        'total_trades': result['total_trades'],
                        'win_rate': result['win_rate'],
                        'total_return': result['total_return'],
                        'profit_factor': result['profit_factor']
                    })
        
        if not results:
            return pd.DataFrame()
        
        return pd.DataFrame(results)

