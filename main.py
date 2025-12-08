"""
미국 주식 매수 신호 생성 시스템
3종류의 매수 신호를 생성하고 최적의 수익률 전략을 제시합니다.
"""
import pandas as pd
from datetime import datetime
import sys
import io

# Windows 콘솔 인코딩 문제 해결
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

from data_fetcher import DataFetcher
from signal_generator import SignalGenerator
from backtester import Backtester
from symbol_fetcher import SymbolFetcher
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import time
from typing import List


class StockSignalSystem:
    """주식 매수 신호 시스템 메인 클래스"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.signal_generator = SignalGenerator()
        self.backtester = Backtester()
        self.symbol_fetcher = SymbolFetcher()
    
    def analyze_symbol(self, symbol: str, timeframe: str = 'short_swing', 
                      skip_backtest: bool = False, silent: bool = False) -> dict:
        """
        심볼을 분석하고 매수 신호를 생성합니다.
        
        Args:
            symbol: 주식 심볼
            timeframe: 시간프레임 ('day_trading', 'short_swing', 'long_swing')
            skip_backtest: 백테스팅 스킵 여부 (속도 향상)
            silent: 출력 억제 여부 (멀티스레딩 시 사용)
        
        Returns:
            분석 결과 딕셔너리
        """
        tf_config = config.TIMEFRAMES[timeframe]
        
        if not silent:
            print(f"\n{'='*60}")
            print(f"📊 {symbol} 분석 중... ({tf_config['name']})")
            print(f"{'='*60}")
        
        # 데이터 수집
        data = self.data_fetcher.fetch_data(
            symbol,
            interval=tf_config['interval'],
            period=tf_config['period']
        )
        
        if data is None or data.empty:
            if not silent:
                print(f"❌ {symbol} 데이터를 가져올 수 없습니다.")
            return None
        
        # 신호 생성
        df_with_signals = self.signal_generator.generate_signals(data)
        
        # 현재 신호 확인
        latest = df_with_signals.iloc[-1]
        current_signal = {
            'symbol': symbol,
            'date': latest.name,
            'price': round(latest['close'], 2),
            'score': latest['signal_score'],
            'level': latest['signal_level'],
            'rsi': round(latest.get('rsi', 0), 2) if not pd.isna(latest.get('rsi')) else None,
            'macd': round(latest.get('macd', 0), 2) if not pd.isna(latest.get('macd')) else None,
            'ma_short': round(latest.get('ma_short', 0), 2) if not pd.isna(latest.get('ma_short')) else None,
            'ma_long': round(latest.get('ma_long', 0), 2) if not pd.isna(latest.get('ma_long')) else None,
        }
        
        # 백테스팅 수행 (스킵 가능)
        backtest_results = {}
        if not skip_backtest:
            for signal_level in ['STRONG_BUY', 'BUY', 'WATCH']:
                min_score = {'STRONG_BUY': 8.0, 'BUY': 5.0, 'WATCH': 3.0}[signal_level]
                result = self.backtester.backtest_strategy(
                    data,
                    signal_level=signal_level,
                    min_score=min_score,
                    hold_days=5,
                    stop_loss=0.05,
                    take_profit=0.10
                )
                if result:
                    backtest_results[signal_level] = result
        
        return {
            'current_signal': current_signal,
            'backtest_results': backtest_results,
            'data': df_with_signals
        }
    
    def display_signal(self, result: dict):
        """신호를 보기 좋게 출력합니다."""
        if result is None:
            return
        
        signal = result['current_signal']
        backtest = result['backtest_results']
        
        # 신호 레벨에 따른 색상 및 이모지
        level_info = config.SIGNAL_LEVELS.get(signal['level'], {})
        level_name = level_info.get('name', signal['level'])
        
        emoji_map = {
            'STRONG_BUY': '🟢',
            'BUY': '🔵',
            'WATCH': '🟡',
            'HOLD': '⚪'
        }
        emoji = emoji_map.get(signal['level'], '⚪')
        
        print(f"\n{emoji} 현재 매수 신호: {level_name}")
        print(f"   점수: {signal['score']}/10")
        print(f"   가격: ${signal['price']}")
        print(f"   날짜: {signal['date']}")
        
        if signal['rsi']:
            print(f"   RSI: {signal['rsi']}")
        if signal['macd']:
            print(f"   MACD: {signal['macd']}")
        
        # 백테스팅 결과 출력
        print(f"\n📈 백테스팅 결과 (과거 데이터 기준):")
        print(f"{'-'*60}")
        
        for level in ['STRONG_BUY', 'BUY', 'WATCH']:
            if level in backtest and backtest[level]['total_trades'] > 0:
                bt = backtest[level]
                level_name_bt = config.SIGNAL_LEVELS[level]['name']
                print(f"\n{level_name_bt} 신호 전략:")
                print(f"   총 거래: {bt['total_trades']}회")
                print(f"   승률: {bt['win_rate']}%")
                print(f"   총 수익률: {bt['total_return']}%")
                print(f"   수익 팩터: {bt['profit_factor']}")
                print(f"   평균 수익: ${bt['avg_win']}")
                print(f"   평균 손실: ${bt['avg_loss']}")
    
    def find_best_strategy(self, symbol: str, timeframe: str = 'short_swing') -> dict:
        """최적의 전략을 찾습니다."""
        tf_config = config.TIMEFRAMES[timeframe]
        
        data = self.data_fetcher.fetch_data(
            symbol,
            interval=tf_config['interval'],
            period=tf_config['period']
        )
        
        if data is None or data.empty:
            return None
        
        # 다양한 전략 비교
        comparison = self.backtester.compare_strategies(
            data,
            hold_days_list=[1, 3, 5, 10, 20],
            stop_loss=0.05,
            take_profit=0.10
        )
        
        if comparison.empty:
            return None
        
        # 최고 수익률 전략 찾기
        best = comparison.loc[comparison['total_return'].idxmax()]
        
        return {
            'best_strategy': best.to_dict(),
            'all_strategies': comparison.to_dict('records')
        }
    
    def analyze_all_timeframes(self, symbol: str) -> dict:
        """
        모든 시간프레임을 분석합니다.
        
        Args:
            symbol: 주식 심볼
        
        Returns:
            모든 시간프레임별 분석 결과
        """
        results = {}
        
        for timeframe_key, timeframe_config in config.TIMEFRAMES.items():
            try:
                data = self.data_fetcher.fetch_data(
                    symbol,
                    interval=timeframe_config['interval'],
                    period=timeframe_config['period']
                )
                
                if data is None or data.empty:
                    continue
                
                # 신호 생성
                df_with_signals = self.signal_generator.generate_signals(data)
                if df_with_signals.empty:
                    continue
                
                latest = df_with_signals.iloc[-1]
                
                # 백테스팅 수행 (각 신호 레벨별)
                backtest_results = {}
                for signal_level in ['STRONG_BUY', 'BUY', 'WATCH']:
                    min_score = {'STRONG_BUY': 8.0, 'BUY': 5.0, 'WATCH': 3.0}[signal_level]
                    result = self.backtester.backtest_strategy(
                        data,
                        signal_level=signal_level,
                        min_score=min_score,
                        hold_days=5,
                        stop_loss=0.05,
                        take_profit=0.10
                    )
                    if result and result['total_trades'] > 0:
                        backtest_results[signal_level] = result
                
                # 최고 수익률 신호 찾기
                best_backtest = None
                best_return = -999
                for level, bt_result in backtest_results.items():
                    if bt_result['total_return'] > best_return:
                        best_return = bt_result['total_return']
                        best_backtest = bt_result
                        best_backtest['signal_level'] = level
                
                results[timeframe_key] = {
                    'name': timeframe_config['name'],
                    'current_signal': {
                        'score': latest['signal_score'],
                        'level': latest['signal_level'],
                        'price': round(latest['close'], 2),
                        'date': latest.name
                    },
                    'backtest_results': backtest_results,
                    'best_backtest': best_backtest,
                    'best_return': best_return if best_backtest else None
                }
                
            except Exception as e:
                print(f"⚠️ {symbol} {timeframe_config['name']} 분석 중 오류: {str(e)}")
                continue
        
        return results
    
    def recommend_timeframe(self, symbol: str) -> dict:
        """
        종목에 가장 적합한 거래 스타일을 추천합니다.
        
        Args:
            symbol: 주식 심볼
        
        Returns:
            추천 결과 딕셔너리
        """
        print(f"\n{'='*60}")
        print(f"🎯 {symbol} 최적 거래 스타일 분석 중...")
        print(f"{'='*60}")
        
        all_results = self.analyze_all_timeframes(symbol)
        
        if not all_results:
            print(f"❌ {symbol}에 대한 분석 데이터가 없습니다.")
            return None
        
        # 각 시간프레임별 최고 수익률 비교
        timeframe_comparison = []
        for tf_key, result in all_results.items():
            if result['best_return'] is not None:
                timeframe_comparison.append({
                    'timeframe': tf_key,
                    'name': result['name'],
                    'best_return': result['best_return'],
                    'current_score': result['current_signal']['score'],
                    'current_level': result['current_signal']['level'],
                    'best_backtest': result['best_backtest']
                })
        
        if not timeframe_comparison:
            print(f"⚠️ {symbol}에 대한 백테스팅 결과가 없습니다.")
            return {
                'symbol': symbol,
                'recommendation': None,
                'all_timeframes': all_results
            }
        
        # 최고 수익률 시간프레임 찾기
        best_timeframe = max(timeframe_comparison, key=lambda x: x['best_return'])
        
        # 현재 신호 점수도 고려한 종합 평가
        # (수익률 70% + 현재 신호 점수 30%)
        for tf in timeframe_comparison:
            normalized_return = (tf['best_return'] + 100) / 200  # -100% ~ +100%를 0~1로 정규화
            normalized_score = tf['current_score'] / 10  # 0~10을 0~1로 정규화
            tf['composite_score'] = normalized_return * 0.7 + normalized_score * 0.3
        
        best_composite = max(timeframe_comparison, key=lambda x: x['composite_score'])
        
        recommendation = {
            'symbol': symbol,
            'recommended_timeframe': best_composite['timeframe'],
            'recommended_name': best_composite['name'],
            'reason': '최고 수익률',
            'expected_return': best_composite['best_return'],
            'current_signal_score': best_composite['current_score'],
            'current_signal_level': best_composite['current_level'],
            'all_timeframes': all_results,
            'comparison': timeframe_comparison
        }
        
        # 결과 출력
        print(f"\n✅ 추천 거래 스타일: {best_composite['name']}")
        print(f"   예상 수익률: {best_composite['best_return']:.2f}%")
        print(f"   현재 신호 점수: {best_composite['current_score']}/10 ({best_composite['current_level']})")
        
        if best_composite['best_backtest']:
            bt = best_composite['best_backtest']
            print(f"\n📊 {best_composite['name']} 백테스팅 상세:")
            print(f"   총 거래: {bt['total_trades']}회")
            print(f"   승률: {bt['win_rate']}%")
            print(f"   수익 팩터: {bt['profit_factor']}")
        
        print(f"\n📋 모든 시간프레임 비교:")
        print(f"{'-'*60}")
        for tf in sorted(timeframe_comparison, key=lambda x: x['best_return'], reverse=True):
            emoji = '🥇' if tf == best_composite else '  '
            print(f"{emoji} {tf['name']:15s} | 수익률: {tf['best_return']:6.2f}% | 현재 점수: {tf['current_score']:4.1f}/10")
        
        return recommendation
    
    def _analyze_single_symbol(self, symbol: str, timeframe: str) -> Optional[dict]:
        """단일 심볼을 분석합니다 (멀티스레딩용 - 백테스팅 스킵, 출력 억제)"""
        try:
            result = self.analyze_symbol(symbol, timeframe, skip_backtest=True, silent=True)
            if result:
                return result['current_signal']
        except Exception as e:
            pass
        return None
    
    def scan_multiple_symbols(self, symbols: list, timeframe: str = 'short_swing', 
                             max_workers: int = 20, show_progress: bool = True):
        """
        여러 심볼을 스캔합니다 (멀티스레딩으로 속도 향상).
        
        Args:
            symbols: 심볼 리스트
            timeframe: 시간프레임
            max_workers: 동시 실행할 최대 스레드 수 (기본값: 10)
            show_progress: 진행 상황 표시 여부
        """
        print(f"\n{'='*60}")
        print(f"🔍 {len(symbols)}개 심볼 스캔 중... (병렬 처리: {max_workers}개 스레드)")
        print(f"{'='*60}\n")
        
        signals = []
        start_time = time.time()
        
        # 멀티스레딩으로 병렬 처리 (API 제한 회피를 위한 요청 간격 추가)
        import time
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 모든 작업 제출 (요청 간격을 두고 제출)
            future_to_symbol = {}
            for i, symbol in enumerate(symbols):
                # 일정 수의 요청 후 잠시 대기 (API 제한 회피)
                if i > 0 and i % (max_workers * 2) == 0:
                    time.sleep(1.0)  # 1초 대기
                elif i > 0 and i % max_workers == 0:
                    time.sleep(0.5)  # 0.5초 대기
                future_to_symbol[executor.submit(self._analyze_single_symbol, symbol, timeframe)] = symbol
            
            # 완료된 작업 처리
            completed = 0
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    signal = future.result()
                    if signal:
                        if signal['level'] in ['STRONG_BUY', 'BUY', 'WATCH']:
                            signals.append(signal)
                            if show_progress:
                                emoji = '🟢' if signal['level'] == 'STRONG_BUY' else '🔵' if signal['level'] == 'BUY' else '🟡'
                                print(f"[{completed}/{len(symbols)}] {emoji} {symbol:6s} | {signal['level']:10s} | 점수: {signal['score']:4.1f}/10")
                        elif show_progress and completed % 10 == 0:
                            # 10개마다 진행 상황만 표시
                            elapsed = time.time() - start_time
                            rate = completed / elapsed if elapsed > 0 else 0
                            remaining = (len(symbols) - completed) / rate if rate > 0 else 0
                            print(f"[{completed}/{len(symbols)}] 진행 중... (예상 남은 시간: {remaining/60:.1f}분)")
                except Exception as e:
                    if show_progress:
                        print(f"[{completed}/{len(symbols)}] ❌ {symbol} 실패")
        
        elapsed_time = time.time() - start_time
        
        # 7.5점 이상 신호만 필터링 (고수익 전략)
        min_score = 7.5
        signals = [s for s in signals if s.get('score', 0) >= min_score]
        
        # 신호 레벨별로 정렬
        level_order = {'STRONG_BUY': 0, 'BUY': 1, 'WATCH': 2, 'HOLD': 3}
        signals.sort(key=lambda x: (level_order.get(x['level'], 99), -x['score']))
        
        # 결과 출력
        print(f"\n{'='*60}")
        print(f"📋 매수 신호 요약 ({len(signals)}개 발견, {min_score}점 이상)")
        print(f"⏱️  소요 시간: {elapsed_time:.1f}초 ({elapsed_time/60:.1f}분)")
        print(f"{'='*60}\n")
        
        emoji_map = {
            'STRONG_BUY': '🟢',
            'BUY': '🔵',
            'WATCH': '🟡'
        }
        
        for signal in signals:
            emoji = emoji_map.get(signal['level'], '⚪')
            level_name = config.SIGNAL_LEVELS[signal['level']]['name']
            print(f"{emoji} {signal['symbol']:6s} | {level_name:8s} | 점수: {signal['score']:4.1f}/10 | 가격: ${signal['price']:8.2f}")
        
        return signals
    
    def scan_index(self, index_name: str = 'sp500', timeframe: str = 'short_swing', limit: Optional[int] = None):
        """
        인덱스(예: S&P 500)의 모든 종목을 스캔합니다.
        
        Args:
            index_name: 'sp500', 'nasdaq100', 'dow30' 중 하나
            timeframe: 시간프레임
            limit: 스캔할 최대 종목 수 (None이면 전체)
        
        Returns:
            매수 신호가 있는 종목 리스트
        """
        print(f"\n{'='*60}")
        print(f"📊 {index_name.upper()} 전체 종목 스캔 시작")
        print(f"{'='*60}\n")
        
        # 인덱스 종목 리스트 가져오기
        symbols = self.symbol_fetcher.get_symbols_by_index(index_name)
        
        if not symbols:
            print(f"❌ {index_name} 종목 리스트를 가져올 수 없습니다.")
            return []
        
        if limit:
            symbols = symbols[:limit]
            print(f"⚠️ 처음 {limit}개 종목만 스캔합니다.\n")
        
        print(f"총 {len(symbols)}개 종목을 스캔합니다.\n")
        
        # 스캔 실행
        return self.scan_multiple_symbols(symbols, timeframe)


def main():
    """메인 실행 함수"""
    system = StockSignalSystem()
    
    print("="*60)
    print("🇺🇸 미국 주식 매수 신호 생성 시스템")
    print("="*60)
    print("\n3종류의 매수 신호:")
    print("  🟢 강한 매수 (STRONG_BUY): 점수 8-10")
    print("  🔵 매수 (BUY): 점수 5-7")
    print("  🟡 관망 매수 (WATCH): 점수 3-4")
    print("\n시간프레임:")
    print("  - day_trading: 데이트레이딩 (5분봉)")
    print("  - short_swing: 단기 스윙 (일봉)")
    print("  - long_swing: 중장기 스윙 (일봉)")
    
    # 예시: 단일 심볼 분석
    print("\n" + "="*60)
    print("예시 분석: AAPL (단기 스윙)")
    print("="*60)
    
    result = system.analyze_symbol('AAPL', 'short_swing')
    system.display_signal(result)
    
    # 최적 거래 스타일 추천 (새로운 기능!)
    print("\n" + "="*60)
    print("최적 거래 스타일 추천")
    print("="*60)
    recommendation = system.recommend_timeframe('AAPL')
    
    # 최적 전략 찾기
    print("\n" + "="*60)
    print("최적 전략 분석")
    print("="*60)
    best = system.find_best_strategy('AAPL', 'short_swing')
    if best:
        bs = best['best_strategy']
        level_name = config.SIGNAL_LEVELS[bs['signal_level']]['name']
        print(f"\n✅ 최고 수익률 전략:")
        print(f"   신호 레벨: {level_name}")
        print(f"   보유 기간: {bs['hold_days']}일")
        print(f"   예상 수익률: {bs['total_return']}%")
        print(f"   승률: {bs['win_rate']}%")
        print(f"   수익 팩터: {bs['profit_factor']}")
    
    # 여러 심볼 스캔
    print("\n" + "="*60)
    print("여러 심볼 스캔")
    print("="*60)
    system.scan_multiple_symbols(config.DEFAULT_SYMBOLS[:5], 'short_swing')
    
    # 전체 인덱스 스캔 예시 (주석 처리 - 시간이 오래 걸릴 수 있음)
    # print("\n" + "="*60)
    # print("S&P 500 전체 스캔 (처음 20개만)")
    # print("="*60)
    # system.scan_index('sp500', 'short_swing', limit=20)


if __name__ == "__main__":
    main()

