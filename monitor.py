"""주식 모니터링"""
import os
import json
import warnings
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_fetcher import fetch_stock_data, YFRateLimitError
from signal_generator import generate_signal
import time

# 경고 억제
warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

class StockMonitor:
    def __init__(self, scan_interval_minutes=240, save_history=True):
        self.scan_interval_minutes = scan_interval_minutes
        self.save_history = save_history
        self.previous_signals = {}
        self.history_file = 'signal_history.json'
        self.load_history()
    
    def load_history(self):
        """이전 신호 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.previous_signals = json.load(f)
        except:
            self.previous_signals = {}
    
    def save_history(self):
        """신호 히스토리 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.previous_signals, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"히스토리 저장 실패: {str(e)}")
    
    def scan_symbol(self, symbol):
        """단일 종목 스캔 (조용한 모드 - 오류 로그 최소화)"""
        try:
            symbol_upper = symbol.upper().strip()
            
            # 특수 문자 필터링
            if '^' in symbol_upper or '/' in symbol_upper or '$' in symbol_upper:
                return None
            
            # 우선주 제외
            if ('.PR' in symbol_upper or 
                symbol_upper.endswith('-P') or 
                any(symbol_upper.endswith(f'-{chr(i)}') for i in range(65, 91))):  # -A ~ -Z
                return None
            
            # 상장폐지 의심 종목 제외 (너무 짧거나 특수 패턴)
            if len(symbol_upper) < 1 or len(symbol_upper) > 5:
                return None
            
            # 조용한 모드로 데이터 가져오기 (오류 로그 없음, 타임아웃 8초로 단축)
            # 주요 종목은 디버깅을 위해 로그 출력
            is_test_symbol = symbol_upper in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META']
            data = fetch_stock_data(symbol, silent=not is_test_symbol, timeout=8)
            if data is None or data.empty:
                if is_test_symbol:
                    print(f"⚠️ {symbol}: 데이터 없음")
                return None
            
            if is_test_symbol:
                print(f"✅ {symbol}: 데이터 가져옴 ({len(data)}개 행)")
            
            # 점수 계산을 먼저 확인
            from signal_generator import calculate_score
            try:
                score = calculate_score(data)
            except Exception as e:
                score = 0
            
            signal = generate_signal(symbol, data)
            
            # 모든 종목의 점수 출력 (5점 이상만 출력하여 로그 과다 방지)
            if score >= 5.0:
                if signal:
                    final_score = signal.get('score', 0)
                    price = signal.get('price', 0)
                    print(f"✅ {symbol}: 신호 생성됨 | 점수: {final_score:.2f}점 | 가격: ${price:.2f}")
                else:
                    print(f"ℹ️ {symbol}: 점수 {score:.2f}점 (7.5점 미만)")
            elif is_test_symbol:
                # 테스트 종목은 점수와 관계없이 출력
                if signal:
                    final_score = signal.get('score', 0)
                    price = signal.get('price', 0)
                    print(f"✅ {symbol}: 신호 생성됨 | 점수: {final_score:.2f}점 | 가격: ${price:.2f}")
                else:
                    print(f"ℹ️ {symbol}: 점수 {score:.2f}점 (7.5점 미만)")
            
            if signal and signal.get('score', 0) >= 7.5:  # 7.5점 이상만
                signal['last_seen'] = signal['date']
                self.previous_signals[symbol] = signal
                print(f"🟢 {symbol}: 7.5점 이상 신호 발견! (점수: {signal.get('score', 0):.2f}점)")
                return signal
            
            return None
            
        except YFRateLimitError:
            # API 제한 시 조용히 대기 (로그 없음)
            time.sleep(10)
            return None
        except Exception as e:
            # 모든 오류는 조용히 무시 (로그 없음)
            return None
    
    def scan_once(self, symbols, timeframe='short_swing', max_workers=20):
        """한 번 스캔 실행"""
        return self.scan_once_with_realtime(symbols, timeframe, max_workers, None)
    
    def scan_once_with_realtime(self, symbols, timeframe='short_swing', max_workers=20, progress_callback=None):
        """실시간 업데이트가 있는 스캔 실행"""
        new_signals = []
        min_score = 7.5
        failed_count = 0
        
        print(f"📊 스캔 시작: {len(symbols)}개 종목")
        print(f"⏳ 첫 번째 종목 처리 중... (잠시만 기다려주세요)")
        print(f"🔧 ThreadPoolExecutor 생성: max_workers={max_workers}")
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                print(f"✅ ThreadPoolExecutor 시작됨, 작업 제출 중...")
                # 모든 작업 제출
                future_to_symbol = {
                    executor.submit(self.scan_symbol, symbol): symbol
                    for symbol in symbols
                }
                print(f"✅ {len(future_to_symbol)}개 작업 제출 완료, 결과 대기 중...")
                print(f"⏰ 첫 번째 결과를 기다리는 중... (타임아웃: 8초)")
                
                completed = 0
                start_time = time.time()
                last_print_time = start_time
                first_result_time = None
                first_wait_start = time.time()
                waiting_printed_5s = False
                waiting_printed_10s = False
                
                for future in as_completed(future_to_symbol):
                    # 첫 번째 결과 대기 시간 체크
                    if first_result_time is None:
                        elapsed = time.time() - first_wait_start
                        if elapsed > 5 and not waiting_printed_5s:
                            print(f"⏳ 첫 번째 결과 대기 중... ({elapsed:.0f}초 경과)")
                            waiting_printed_5s = True
                        elif elapsed > 10 and not waiting_printed_10s:
                            print(f"⚠️ 첫 번째 결과가 10초 이상 지연 중... (yfinance API 응답 지연 또는 차단 가능)")
                            waiting_printed_10s = True
                        elif elapsed > 15:
                            print(f"❌ 첫 번째 결과가 15초 이상 지연 중... API가 차단되었을 가능성이 높습니다.")
                    
                    if first_result_time is None:
                        first_result_time = time.time()
                        wait_time = first_result_time - start_time
                        print(f"✅ 첫 번째 결과 수신! (대기 시간: {wait_time:.1f}초)")
                    
                    completed += 1
                    symbol = future_to_symbol[future]
                    
                    try:
                        signal = future.result()
                        if signal:
                            # 새로운 신호인지 확인
                            is_new = symbol not in self.previous_signals
                            is_higher_score = not is_new and self.previous_signals[symbol].get('score', 0) < signal.get('score', 0)
                            
                            if is_new or is_higher_score:
                                new_signals.append(signal)
                                # 신호 발견 시 즉시 출력
                                if signal.get('score', 0) >= min_score:
                                    print(f"🟢 신호 발견: {symbol} ({signal.get('score', 0)}점) - 가격: ${signal.get('price', 0):.2f}")
                                # 실시간 콜백 호출
                                if progress_callback:
                                    progress_callback(completed, len(symbols), signal)
                        else:
                            failed_count += 1
                    except Exception as e:
                        failed_count += 1
                        pass
                    
                    # 진행률 출력 및 콜백
                    current_time = time.time()
                    time_since_last_print = current_time - last_print_time
                    
                    should_print = False
                    # 처음 10개는 즉시 출력
                    if completed <= 10:
                        should_print = True
                    # 10개 이후는 25개마다 또는 10초마다
                    elif completed <= 100:
                        should_print = (completed % 25 == 0) or (time_since_last_print >= 10)
                    # 100개 이후는 50개마다 또는 15초마다
                    else:
                        should_print = (completed % 50 == 0) or (time_since_last_print >= 15)
                    
                    if should_print:
                        last_print_time = current_time
                        success_rate = ((completed - failed_count) / completed * 100) if completed > 0 else 0
                        percent = completed * 100 // len(symbols) if len(symbols) > 0 else 0
                        elapsed = current_time - start_time
                        remaining = (elapsed / completed * (len(symbols) - completed)) if completed > 0 else 0
                        print(f"📊 진행률: {completed}/{len(symbols)} ({percent}%) | 성공: {completed - failed_count}개, 실패: {failed_count}개 | 성공률: {success_rate:.1f}% | 예상 남은 시간: {remaining/60:.1f}분")
                        if progress_callback:
                            progress_callback(completed, len(symbols), None)
        except Exception as e:
            print(f"❌ ThreadPoolExecutor 실행 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            completed = 0
            failed_count = len(symbols)
            new_signals = []
            filtered_signals = []
        
        # 히스토리 저장
        if self.save_history:
            try:
                self.save_history()
            except Exception as e:
                print(f"⚠️ 히스토리 저장 실패: {str(e)}")
        
        # 7.5점 이상만 필터링
        filtered_signals = [s for s in new_signals if s.get('score', 0) >= min_score]
        
        success_count = completed - failed_count
        elapsed_time = time.time() - start_time
        avg_time_per_symbol = elapsed_time / completed if completed > 0 else 0
        
        print(f"\n{'='*50}")
        print(f"✅ 스캔 완료!")
        print(f"   - 총 종목: {len(symbols)}개")
        print(f"   - 완료: {completed}개")
        print(f"   - 성공: {success_count}개")
        print(f"   - 실패: {failed_count}개 (상장폐지/데이터없음)")
        print(f"   - 새로운 신호: {len(filtered_signals)}개 (7.5점 이상)")
        print(f"   - 소요 시간: {elapsed_time/60:.1f}분 ({elapsed_time:.0f}초)")
        print(f"   - 평균 속도: {avg_time_per_symbol:.2f}초/종목")
        print(f"{'='*50}\n")
        
        return filtered_signals

