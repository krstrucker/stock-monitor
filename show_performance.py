"""
성과 통계 표시 스크립트
현재 모니터링 중인 종목들의 신호 성과를 분석합니다.
"""
import os
import sys
import json
from performance_stats import PerformanceStats
import config

def main():
    print("="*60)
    print("주식 매수 신호 성과 통계 분석")
    print("="*60)
    
    # 모니터링 중인 종목 확인
    signal_history_file = 'signal_history.json'
    symbols_to_analyze = []
    
    if os.path.exists(signal_history_file):
        try:
            with open(signal_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                symbols_to_analyze = list(history.keys())
                print(f"\n신호 이력에서 {len(symbols_to_analyze)}개 종목 발견")
        except:
            pass
    
    # 신호 이력이 없으면 기본 종목 사용
    if not symbols_to_analyze:
        symbol_count = int(os.environ.get('MONITOR_SYMBOL_COUNT', '100'))
        symbols_to_analyze = config.DEFAULT_SYMBOLS[:symbol_count]
        print(f"\n기본 종목 리스트에서 {len(symbols_to_analyze)}개 종목 사용")
    
    # 샘플링 (전체 분석은 시간이 오래 걸림)
    sample_size = min(50, len(symbols_to_analyze))
    symbols_to_analyze = symbols_to_analyze[:sample_size]
    
    print(f"\n분석할 종목 수: {sample_size}개 (샘플링)")
    print("="*60)
    
    # 성과 통계 계산
    stats = PerformanceStats()
    results = stats.get_overall_statistics(symbols_to_analyze, 'short_swing')
    
    # 결과 출력
    print("\n" + "="*60)
    print("전체 성과 통계")
    print("="*60)
    
    overall = results['overall']
    print(f"\n총 거래 횟수: {overall['total_trades']}회")
    print(f"승리 거래: {overall['winning_trades']}회")
    print(f"손실 거래: {overall['losing_trades']}회")
    print(f"\n성공 확률 (승률): {overall['win_rate']}%")
    print(f"\n최저 수익률: {overall['min_return']}%")
    print(f"평균 수익률: {overall['avg_return']}%")
    print(f"최고 수익률: {overall['max_return']}%")
    print(f"총 수익률: {overall['total_return']}%")
    print(f"수익 팩터: {overall['profit_factor']}")
    
    # 신호 레벨별 통계
    print("\n" + "="*60)
    print("신호 레벨별 성과 통계")
    print("="*60)
    
    by_level = results['by_level']
    for level in ['STRONG_BUY', 'BUY', 'WATCH']:
        if level in by_level:
            level_stat = by_level[level]
            print(f"\n[{level}]")
            print(f"  거래 횟수: {level_stat['total_trades']}회")
            print(f"  승률: {level_stat['win_rate']}%")
            print(f"  최저 수익률: {level_stat['min_return']}%")
            print(f"  평균 수익률: {level_stat['avg_return']}%")
            print(f"  최고 수익률: {level_stat['max_return']}%")
            print(f"  수익 팩터: {level_stat['profit_factor']}")
    
    print("\n" + "="*60)
    print(f"분석 완료 (총 {results['analyzed_symbols']}개 종목 분석)")
    print("="*60)

if __name__ == '__main__':
    main()

