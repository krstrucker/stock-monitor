"""
성과 통계 분석 모듈
신호별 수익률 통계를 계산합니다.
"""
import pandas as pd
from typing import Dict, List, Optional
from backtester import Backtester
from data_fetcher import DataFetcher
import config


class PerformanceStats:
    """성과 통계 분석 클래스"""
    
    def __init__(self):
        self.backtester = Backtester()
        self.data_fetcher = DataFetcher()
    
    def analyze_signal_performance(self, symbol: str, timeframe: str = 'short_swing') -> Optional[Dict]:
        """
        특정 종목의 신호별 성과를 분석합니다.
        
        Args:
            symbol: 주식 심볼
            timeframe: 시간프레임
        
        Returns:
            신호별 성과 통계 딕셔너리
        """
        tf_config = config.TIMEFRAMES[timeframe]
        
        # 데이터 가져오기
        data = self.data_fetcher.fetch_data(
            symbol,
            interval=tf_config['interval'],
            period=tf_config['period']
        )
        
        if data is None or data.empty:
            return None
        
        # 각 신호 레벨별로 백테스팅
        results = {}
        for signal_level in ['STRONG_BUY', 'BUY', 'WATCH']:
            min_score = {'STRONG_BUY': 8.0, 'BUY': 5.0, 'WATCH': 3.0}[signal_level]
            
            backtest_result = self.backtester.backtest_strategy(
                data,
                signal_level=signal_level,
                min_score=min_score,
                hold_days=5,
                stop_loss=0.05,
                take_profit=0.10
            )
            
            if backtest_result:
                results[signal_level] = backtest_result
        
        return results
    
    def calculate_statistics(self, backtest_results: List[Dict]) -> Dict:
        """
        백테스팅 결과들의 통계를 계산합니다.
        
        Args:
            backtest_results: 백테스팅 결과 리스트
        
        Returns:
            통계 딕셔너리
        """
        if not backtest_results:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'min_return': 0,
                'max_return': 0,
                'avg_return': 0,
                'total_return': 0,
                'profit_factor': 0
            }
        
        all_returns = []
        winning_trades = 0
        losing_trades = 0
        total_profit = 0
        total_loss = 0
        
        for result in backtest_results:
            if 'positions' in result and result['positions']:
                for position in result['positions']:
                    if 'pnl_ratio' in position:
                        return_pct = position['pnl_ratio']  # 백테스터는 pnl_ratio를 %로 반환
                        all_returns.append(return_pct)
                        
                        if return_pct > 0:
                            winning_trades += 1
                            total_profit += return_pct
                        else:
                            losing_trades += 1
                            total_loss += abs(return_pct)
        
        total_trades = len(all_returns)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        min_return = min(all_returns) if all_returns else 0
        max_return = max(all_returns) if all_returns else 0
        avg_return = sum(all_returns) / len(all_returns) if all_returns else 0
        total_return = sum(all_returns) if all_returns else 0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else (total_profit if total_profit > 0 else 0)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'min_return': round(min_return, 2),
            'max_return': round(max_return, 2),
            'avg_return': round(avg_return, 2),
            'total_return': round(total_return, 2),
            'profit_factor': round(profit_factor, 2)
        }
    
    def get_overall_statistics(self, symbols: List[str], timeframe: str = 'short_swing') -> Dict:
        """
        여러 종목의 전체 성과 통계를 계산합니다.
        
        Args:
            symbols: 종목 리스트
            timeframe: 시간프레임
        
        Returns:
            전체 통계 딕셔너리
        """
        all_results = []
        symbol_results = {}  # 종목별 결과 저장
        
        print(f"\n{'='*60}")
        print(f"전체 성과 통계 계산 중... ({len(symbols)}개 종목)")
        print(f"{'='*60}\n")
        
        for i, symbol in enumerate(symbols, 1):
            if i % 100 == 0:
                print(f"진행: {i}/{len(symbols)} 종목 분석 완료...")
            
            try:
                results = self.analyze_signal_performance(symbol, timeframe)
                if results:
                    symbol_results[symbol] = results
                    # 각 신호 레벨별 결과를 리스트에 추가
                    for signal_level, result in results.items():
                        if result and 'positions' in result:
                            all_results.append(result)
            except:
                pass
        
        # 전체 통계 계산
        overall_stats = self.calculate_statistics(all_results)
        
        # 신호 레벨별 통계
        level_stats = {}
        for signal_level in ['STRONG_BUY', 'BUY', 'WATCH']:
            level_results = []
            for symbol_result in symbol_results.values():
                if signal_level in symbol_result and symbol_result[signal_level]:
                    level_results.append(symbol_result[signal_level])
            if level_results:
                level_stats[signal_level] = self.calculate_statistics(level_results)
        
        return {
            'overall': overall_stats,
            'by_level': level_stats,
            'analyzed_symbols': len(symbols)
        }

