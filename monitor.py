"""주식 모니터링"""
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_fetcher import fetch_stock_data, YFRateLimitError
from signal_generator import generate_signal
import time

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
        """단일 종목 스캔"""
        try:
            # 특수 문자 필터링
            if '^' in symbol or '/' in symbol or '$' in symbol:
                return None
            
            data = fetch_stock_data(symbol)
            if data is None or data.empty:
                return None
            
            signal = generate_signal(symbol, data)
            
            if signal and signal.get('score', 0) >= 7.5:  # 7.5점 이상만
                signal['last_seen'] = signal['date']
                self.previous_signals[symbol] = signal
                return signal
            
            return None
        except YFRateLimitError:
            # API 제한 시 대기
            time.sleep(5)
            return None
        except Exception as e:
            return None
    
    def scan_once(self, symbols, timeframe='short_swing', max_workers=20):
        """한 번 스캔 실행"""
        new_signals = []
        min_score = 7.5
        
        print(f"📊 스캔 시작: {len(symbols)}개 종목")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.scan_symbol, symbol): symbol
                for symbol in symbols
            }
            
            completed = 0
            for future in as_completed(future_to_symbol):
                completed += 1
                symbol = future_to_symbol[future]
                
                try:
                    signal = future.result()
                    if signal:
                        # 새로운 신호인지 확인
                        if symbol not in self.previous_signals:
                            new_signals.append(signal)
                        elif self.previous_signals[symbol].get('score', 0) < signal.get('score', 0):
                            # 점수가 더 높아진 경우
                            new_signals.append(signal)
                except Exception as e:
                    pass
                
                if completed % 100 == 0:
                    print(f"진행률: {completed}/{len(symbols)} ({completed*100//len(symbols)}%)")
        
        # 히스토리 저장
        if self.save_history:
            self.save_history()
        
        # 7.5점 이상만 필터링
        filtered_signals = [s for s in new_signals if s.get('score', 0) >= min_score]
        
        print(f"✅ 스캔 완료: {len(filtered_signals)}개 새로운 신호 (7.5점 이상)")
        
        return filtered_signals

