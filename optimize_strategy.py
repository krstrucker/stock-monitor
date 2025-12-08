"""
전략 최적화 스크립트
1년에 평균 50% 이상 수익을 낼 수 있는 최적 전략을 찾습니다.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from backtester import Backtester
from data_fetcher import DataFetcher
from signal_generator import SignalGenerator
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class StrategyOptimizer:
    """전략 최적화 클래스"""
    
    def __init__(self):
        self.backtester = Backtester()
        self.data_fetcher = DataFetcher()
        self.signal_generator = SignalGenerator()
    
    def calculate_annual_return(self, total_return: float, period_days: int) -> float:
        """
        연간 수익률을 계산합니다.
        
        Args:
            total_return: 총 수익률 (%)
            period_days: 기간 (일)
        
        Returns:
            연간 수익률 (%)
        """
        if period_days <= 0:
            return 0
        
        # 복리 계산
        daily_return = (1 + total_return / 100) ** (1 / period_days)
        annual_return = (daily_return ** 365 - 1) * 100
        
        return annual_return
    
    def test_strategy(self, 
                     symbol: str,
                     signal_level: str,
                     min_score: float,
                     hold_days: int,
                     stop_loss: float,
                     take_profit: float,
                     timeframe: str = 'short_swing') -> Dict:
        """
        특정 전략을 테스트합니다.
        
        Returns:
            전략 테스트 결과
        """
        try:
            tf_config = config.TIMEFRAMES[timeframe]
            
            # 데이터 가져오기
            data = self.data_fetcher.fetch_data(
                symbol,
                interval=tf_config['interval'],
                period=tf_config['period']
            )
            
            if data is None or data.empty:
                return None
            
            # 백테스팅 수행
            result = self.backtester.backtest_strategy(
                data,
                signal_level=signal_level,
                min_score=min_score,
                hold_days=hold_days,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if not result or result['total_trades'] == 0:
                return None
            
            # 기간 계산
            if len(data) > 0:
                period_days = (data.index[-1] - data.index[0]).days if hasattr(data.index[-1] - data.index[0], 'days') else 90
            else:
                period_days = 90
            
            # 연간 수익률 계산
            annual_return = self.calculate_annual_return(result['total_return'], period_days)
            
            return {
                'symbol': symbol,
                'signal_level': signal_level,
                'min_score': min_score,
                'hold_days': hold_days,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'total_trades': result['total_trades'],
                'win_rate': result['win_rate'],
                'total_return': result['total_return'],
                'annual_return': annual_return,
                'profit_factor': result['profit_factor'],
                'period_days': period_days
            }
        except:
            return None
    
    def optimize_for_high_return(self, 
                                symbols: List[str],
                                target_annual_return: float = 50.0,
                                timeframe: str = 'short_swing') -> Dict:
        """
        높은 수익률을 위한 전략을 최적화합니다.
        
        Args:
            symbols: 테스트할 종목 리스트
            target_annual_return: 목표 연간 수익률 (%)
            timeframe: 시간프레임
        
        Returns:
            최적 전략 결과
        """
        print(f"\n{'='*60}")
        print(f"전략 최적화 시작 (목표: 연간 {target_annual_return}% 이상)")
        print(f"{'='*60}\n")
        
        # 테스트할 전략 파라미터 조합
        strategies = []
        
        # STRONG_BUY만 집중 (더 엄격한 기준, 더 높은 익절)
        for min_score in [8.5, 9.0, 9.5]:
            for hold_days in [5, 7, 10, 14, 20]:
                for stop_loss in [0.03, 0.05, 0.07]:  # 더 타이트한 손절
                    for take_profit in [0.25, 0.30, 0.35, 0.40, 0.50]:  # 더 높은 익절 (50%까지)
                        strategies.append({
                            'signal_level': 'STRONG_BUY',
                            'min_score': min_score,
                            'hold_days': hold_days,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit
                        })
        
        # BUY 신호도 테스트 (더 높은 점수 기준, 더 높은 익절)
        for min_score in [6.5, 7.0, 7.5, 8.0]:
            for hold_days in [7, 10, 14, 20, 30]:
                for stop_loss in [0.05, 0.07]:
                    for take_profit in [0.25, 0.30, 0.35, 0.40, 0.50]:
                        strategies.append({
                            'signal_level': 'BUY',
                            'min_score': min_score,
                            'hold_days': hold_days,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit
                        })
        
        print(f"총 {len(strategies)}개 전략 조합 테스트 중...")
        print(f"테스트 종목 수: {len(symbols)}개\n")
        
        # 각 전략별로 종목 테스트
        strategy_results = {}
        
        for idx, strategy in enumerate(strategies, 1):
            if idx % 50 == 0:
                print(f"진행: {idx}/{len(strategies)} 전략 테스트 완료...")
            
            strategy_key = f"{strategy['signal_level']}_score{strategy['min_score']}_hold{strategy['hold_days']}_sl{strategy['stop_loss']}_tp{strategy['take_profit']}"
            
            annual_returns = []
            win_rates = []
            trade_counts = []
            profit_factors = []
            
            # 샘플 종목으로 테스트 (전체는 시간이 오래 걸림)
            sample_symbols = symbols[:min(30, len(symbols))]
            
            for symbol in sample_symbols:
                result = self.test_strategy(
                    symbol,
                    **strategy,
                    timeframe=timeframe
                )
                
                if result and result['annual_return'] > 0:
                    annual_returns.append(result['annual_return'])
                    win_rates.append(result['win_rate'])
                    trade_counts.append(result['total_trades'])
                    profit_factors.append(result['profit_factor'])
            
            if annual_returns:
                avg_annual_return = np.mean(annual_returns)
                avg_win_rate = np.mean(win_rates)
                total_trades = sum(trade_counts)
                avg_profit_factor = np.mean(profit_factors)
                
                strategy_results[strategy_key] = {
                    'strategy': strategy,
                    'avg_annual_return': avg_annual_return,
                    'avg_win_rate': avg_win_rate,
                    'total_trades': total_trades,
                    'avg_profit_factor': avg_profit_factor,
                    'sample_size': len(annual_returns)
                }
        
        # 목표 수익률 이상인 전략 필터링
        qualified_strategies = {
            k: v for k, v in strategy_results.items()
            if v['avg_annual_return'] >= target_annual_return
        }
        
        # 연간 수익률 기준으로 정렬
        sorted_strategies = sorted(
            qualified_strategies.items(),
            key=lambda x: x[1]['avg_annual_return'],
            reverse=True
        )
        
        return {
            'qualified_strategies': dict(sorted_strategies[:20]),  # 상위 20개만
            'total_tested': len(strategies),
            'qualified_count': len(qualified_strategies),
            'target_return': target_annual_return
        }
    
    def recommend_best_strategy(self, symbols: List[str], timeframe: str = 'short_swing') -> Dict:
        """
        최적의 전략을 추천합니다.
        
        Returns:
            추천 전략 정보
        """
        print("\n" + "="*60)
        print("최적 전략 탐색 중...")
        print("="*60)
        
        # 50% 목표로 최적화
        results = self.optimize_for_high_return(symbols, target_annual_return=50.0, timeframe=timeframe)
        
        if not results['qualified_strategies']:
            print("\n⚠️ 목표 수익률(50%)을 달성하는 전략을 찾지 못했습니다.")
            print("더 낮은 목표로 재시도합니다...\n")
            results = self.optimize_for_high_return(symbols, target_annual_return=30.0, timeframe=timeframe)
        
        return results


def main():
    import os
    import json
    
    print("="*60)
    print("1년 평균 50% 이상 수익 전략 최적화")
    print("="*60)
    
    # 종목 리스트 가져오기
    signal_history_file = 'signal_history.json'
    symbols = []
    
    if os.path.exists(signal_history_file):
        try:
            with open(signal_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                symbols = list(history.keys())
        except:
            pass
    
    if not symbols:
        symbol_count = int(os.environ.get('MONITOR_SYMBOL_COUNT', '100'))
        symbols = config.DEFAULT_SYMBOLS[:symbol_count]
    
    # 샘플링 (전체는 시간이 오래 걸림)
    sample_size = min(50, len(symbols))
    symbols = symbols[:sample_size]
    
    print(f"\n테스트 종목 수: {len(symbols)}개")
    
    # 최적화 수행
    optimizer = StrategyOptimizer()
    results = optimizer.recommend_best_strategy(symbols, 'short_swing')
    
    # 결과 출력
    print("\n" + "="*60)
    print("최적 전략 추천 결과")
    print("="*60)
    
    if results['qualified_strategies']:
        print(f"\n✅ 목표 수익률 달성 전략: {results['qualified_count']}개 발견")
        print(f"테스트한 전략 수: {results['total_tested']}개\n")
        
        # 상위 5개 전략 출력
        top_strategies = list(results['qualified_strategies'].items())[:5]
        
        for i, (key, data) in enumerate(top_strategies, 1):
            strategy = data['strategy']
            print(f"\n[추천 전략 #{i}]")
            print(f"  신호 레벨: {strategy['signal_level']}")
            print(f"  최소 점수: {strategy['min_score']}")
            print(f"  보유 기간: {strategy['hold_days']}일")
            print(f"  손절매: {strategy['stop_loss']*100}%")
            print(f"  익절매: {strategy['take_profit']*100}%")
            print(f"  예상 연간 수익률: {data['avg_annual_return']:.2f}%")
            print(f"  평균 승률: {data['avg_win_rate']:.2f}%")
            print(f"  총 거래 횟수: {data['total_trades']}회")
            print(f"  수익 팩터: {data['avg_profit_factor']:.2f}")
        
        # 최고 전략 추천
        best_key, best_data = top_strategies[0]
        best_strategy = best_data['strategy']
        
        print("\n" + "="*60)
        print("🏆 최고 추천 전략")
        print("="*60)
        print(f"\n신호 레벨: {best_strategy['signal_level']}")
        print(f"최소 점수: {best_strategy['min_score']} 이상")
        print(f"보유 기간: {best_strategy['hold_days']}일")
        print(f"손절매: {best_strategy['stop_loss']*100}%")
        print(f"익절매: {best_strategy['take_profit']*100}%")
        print(f"\n예상 성과:")
        print(f"  연간 수익률: {best_data['avg_annual_return']:.2f}%")
        print(f"  평균 승률: {best_data['avg_win_rate']:.2f}%")
        print(f"  수익 팩터: {best_data['avg_profit_factor']:.2f}")
        
        # 설정 파일 생성 제안
        print("\n" + "="*60)
        print("설정 적용 방법")
        print("="*60)
        print("\n이 전략을 사용하려면 config.py에서 다음을 수정하세요:")
        print(f"\nSIGNAL_THRESHOLDS = {{")
        print(f"    'STRONG_BUY': {best_strategy['min_score'] if best_strategy['signal_level'] == 'STRONG_BUY' else 8.0},")
        print(f"    'BUY': {best_strategy['min_score'] if best_strategy['signal_level'] == 'BUY' else 5.0},")
        print(f"    'WATCH': 3.0")
        print(f"}}")
        print(f"\n백테스팅 파라미터:")
        print(f"  hold_days = {best_strategy['hold_days']}")
        print(f"  stop_loss = {best_strategy['stop_loss']}")
        print(f"  take_profit = {best_strategy['take_profit']}")
        
    else:
        print("\n⚠️ 목표 수익률을 달성하는 전략을 찾지 못했습니다.")
        print("\n제안:")
        print("1. 더 엄격한 신호 필터링 (최소 점수 상향)")
        print("2. 더 긴 보유 기간 설정")
        print("3. 더 높은 익절 목표 설정")
        print("4. 더 타이트한 손절 설정")


if __name__ == '__main__':
    main()

