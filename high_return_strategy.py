"""
고수익 전략 추천 스크립트
1년에 50% 이상 수익을 위한 최적 전략을 찾습니다.
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from backtester import Backtester
from data_fetcher import DataFetcher
import config
import json
import os


class HighReturnStrategy:
    """고수익 전략 클래스"""
    
    def __init__(self):
        self.backtester = Backtester()
        self.data_fetcher = DataFetcher()
    
    def calculate_compound_return(self, returns: List[float]) -> float:
        """
        복리 수익률을 계산합니다.
        
        Args:
            returns: 각 거래의 수익률 리스트 (%)
        
        Returns:
            총 복리 수익률 (%)
        """
        if not returns:
            return 0
        
        compound = 1.0
        for ret in returns:
            compound *= (1 + ret / 100)
        
        return (compound - 1) * 100
    
    def test_aggressive_strategy(self, symbol: str) -> Dict:
        """
        공격적인 고수익 전략을 테스트합니다.
        
        전략:
        - STRONG_BUY만 선택 (점수 9.0 이상)
        - 보유 기간: 10-20일
        - 손절: 5%
        - 익절: 30-50%
        """
        try:
            # 1년 데이터 사용
            data = self.data_fetcher.fetch_data(symbol, interval='1d', period='1y')
            
            if data is None or data.empty:
                return None
            
            # 여러 전략 테스트
            strategies = [
                {
                    'name': '공격적 STRONG_BUY',
                    'signal_level': 'STRONG_BUY',
                    'min_score': 9.0,
                    'hold_days': 10,
                    'stop_loss': 0.05,
                    'take_profit': 0.30
                },
                {
                    'name': '매우 공격적 STRONG_BUY',
                    'signal_level': 'STRONG_BUY',
                    'min_score': 9.0,
                    'hold_days': 14,
                    'stop_loss': 0.05,
                    'take_profit': 0.40
                },
                {
                    'name': '극도 공격적 STRONG_BUY',
                    'signal_level': 'STRONG_BUY',
                    'min_score': 9.5,
                    'hold_days': 20,
                    'stop_loss': 0.05,
                    'take_profit': 0.50
                },
                {
                    'name': '고점수 BUY',
                    'signal_level': 'BUY',
                    'min_score': 7.5,
                    'hold_days': 14,
                    'stop_loss': 0.05,
                    'take_profit': 0.35
                },
                {
                    'name': '초고점수 BUY',
                    'signal_level': 'BUY',
                    'min_score': 8.0,
                    'hold_days': 20,
                    'stop_loss': 0.05,
                    'take_profit': 0.40
                }
            ]
            
            best_strategy = None
            best_annual_return = -999
            
            for strategy in strategies:
                result = self.backtester.backtest_strategy(
                    data,
                    signal_level=strategy['signal_level'],
                    min_score=strategy['min_score'],
                    hold_days=strategy['hold_days'],
                    stop_loss=strategy['stop_loss'],
                    take_profit=strategy['take_profit']
                )
                
                if result and result['total_trades'] > 0:
                    # 연간 수익률 계산
                    period_days = (data.index[-1] - data.index[0]).days if hasattr(data.index[-1] - data.index[0], 'days') else 365
                    annual_return = ((1 + result['total_return'] / 100) ** (365 / period_days) - 1) * 100
                    
                    # 복리 효과 고려 (각 거래의 수익률로 계산)
                    if result['positions']:
                        returns = [p['pnl_ratio'] for p in result['positions']]
                        compound_return = self.calculate_compound_return(returns)
                        annual_compound = ((1 + compound_return / 100) ** (365 / period_days) - 1) * 100
                    else:
                        annual_compound = annual_return
                    
                    if annual_compound > best_annual_return:
                        best_annual_return = annual_compound
                        best_strategy = {
                            **strategy,
                            'result': result,
                            'annual_return': annual_return,
                            'annual_compound_return': annual_compound,
                            'period_days': period_days
                        }
            
            return best_strategy
            
        except Exception as e:
            return None
    
    def analyze_multiple_symbols(self, symbols: List[str], top_n: int = 20) -> Dict:
        """
        여러 종목을 분석하여 최고 수익 전략을 찾습니다.
        """
        print(f"\n{'='*60}")
        print(f"고수익 전략 분석 중... ({len(symbols)}개 종목)")
        print(f"{'='*60}\n")
        
        strategy_performance = {}
        
        for i, symbol in enumerate(symbols, 1):
            if i % 10 == 0:
                print(f"진행: {i}/{len(symbols)} 종목 분석 완료...")
            
            result = self.test_aggressive_strategy(symbol)
            
            if result and result['annual_compound_return'] > 0:
                strategy_key = f"{result['signal_level']}_score{result['min_score']}_hold{result['hold_days']}_tp{result['take_profit']}"
                
                if strategy_key not in strategy_performance:
                    strategy_performance[strategy_key] = {
                        'strategy': result,
                        'annual_returns': [],
                        'win_rates': [],
                        'trade_counts': [],
                        'symbols': []
                    }
                
                strategy_performance[strategy_key]['annual_returns'].append(result['annual_compound_return'])
                strategy_performance[strategy_key]['win_rates'].append(result['result']['win_rate'])
                strategy_performance[strategy_key]['trade_counts'].append(result['result']['total_trades'])
                strategy_performance[strategy_key]['symbols'].append(symbol)
        
        # 각 전략별 평균 계산
        strategy_stats = {}
        for key, data in strategy_performance.items():
            if data['annual_returns']:
                strategy_stats[key] = {
                    'strategy': data['strategy'],
                    'avg_annual_return': np.mean(data['annual_returns']),
                    'median_annual_return': np.median(data['annual_returns']),
                    'max_annual_return': np.max(data['annual_returns']),
                    'avg_win_rate': np.mean(data['win_rates']),
                    'total_trades': sum(data['trade_counts']),
                    'sample_size': len(data['annual_returns']),
                    'symbols': data['symbols']
                }
        
        # 연간 수익률 기준으로 정렬
        sorted_strategies = sorted(
            strategy_stats.items(),
            key=lambda x: x[1]['avg_annual_return'],
            reverse=True
        )
        
        return {
            'strategies': dict(sorted_strategies[:top_n]),
            'total_analyzed': len(symbols)
        }


def main():
    print("="*60)
    print("1년 평균 50% 이상 수익 전략 분석")
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
    
    # 샘플링
    sample_size = min(100, len(symbols))
    symbols = symbols[:sample_size]
    
    print(f"\n분석할 종목 수: {len(symbols)}개")
    
    # 고수익 전략 분석
    analyzer = HighReturnStrategy()
    results = analyzer.analyze_multiple_symbols(symbols, top_n=10)
    
    # 결과 출력
    print("\n" + "="*60)
    print("고수익 전략 추천 결과")
    print("="*60)
    
    if results['strategies']:
        print(f"\n총 {len(results['strategies'])}개 전략 발견\n")
        
        # 상위 5개 전략 출력
        top_strategies = list(results['strategies'].items())[:5]
        
        for i, (key, data) in enumerate(top_strategies, 1):
            strategy = data['strategy']
            print(f"\n[추천 전략 #{i}]")
            print(f"  전략명: {strategy['name']}")
            print(f"  신호 레벨: {strategy['signal_level']}")
            print(f"  최소 점수: {strategy['min_score']}")
            print(f"  보유 기간: {strategy['hold_days']}일")
            print(f"  손절매: {strategy['stop_loss']*100}%")
            print(f"  익절매: {strategy['take_profit']*100}%")
            print(f"  평균 연간 수익률: {data['avg_annual_return']:.2f}%")
            print(f"  중간값 연간 수익률: {data['median_annual_return']:.2f}%")
            print(f"  최고 연간 수익률: {data['max_annual_return']:.2f}%")
            print(f"  평균 승률: {data['avg_win_rate']:.2f}%")
            print(f"  총 거래 횟수: {data['total_trades']}회")
            print(f"  테스트 종목 수: {data['sample_size']}개")
        
        # 최고 전략 추천
        best_key, best_data = top_strategies[0]
        best_strategy = best_data['strategy']
        
        print("\n" + "="*60)
        print("최고 추천 전략")
        print("="*60)
        print(f"\n전략명: {best_strategy['name']}")
        print(f"신호 레벨: {best_strategy['signal_level']}")
        print(f"최소 점수: {best_strategy['min_score']} 이상")
        print(f"보유 기간: {best_strategy['hold_days']}일")
        print(f"손절매: {best_strategy['stop_loss']*100}%")
        print(f"익절매: {best_strategy['take_profit']*100}%")
        print(f"\n예상 성과:")
        print(f"  평균 연간 수익률: {best_data['avg_annual_return']:.2f}%")
        print(f"  중간값 연간 수익률: {best_data['median_annual_return']:.2f}%")
        print(f"  최고 연간 수익률: {best_data['max_annual_return']:.2f}%")
        print(f"  평균 승률: {best_data['avg_win_rate']:.2f}%")
        print(f"  총 거래 횟수: {best_data['total_trades']}회")
        
        # 50% 이상 달성 여부 확인
        if best_data['avg_annual_return'] >= 50.0:
            print(f"\n✅ 목표 달성! 평균 연간 수익률 {best_data['avg_annual_return']:.2f}%")
        elif best_data['max_annual_return'] >= 50.0:
            print(f"\n⚠️ 일부 종목에서 50% 이상 달성 (최고: {best_data['max_annual_return']:.2f}%)")
            print(f"   평균: {best_data['avg_annual_return']:.2f}%")
        else:
            print(f"\n⚠️ 50% 목표 미달성")
            print(f"   최고: {best_data['max_annual_return']:.2f}%, 평균: {best_data['avg_annual_return']:.2f}%")
        
        print("\n" + "="*60)
        print("설정 적용 방법")
        print("="*60)
        print("\n이 전략을 사용하려면:")
        print(f"1. STRONG_BUY 신호만 선택 (점수 {best_strategy['min_score']} 이상)")
        print(f"2. 보유 기간: {best_strategy['hold_days']}일")
        print(f"3. 손절매: {best_strategy['stop_loss']*100}%")
        print(f"4. 익절매: {best_strategy['take_profit']*100}%")
        print("\n또는 config.py에서 신호 기준을 조정하세요.")
        
    else:
        print("\n⚠️ 분석 결과가 없습니다.")


if __name__ == '__main__':
    main()

