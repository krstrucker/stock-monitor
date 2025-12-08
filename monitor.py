"""
자동 모니터링 시스템
주기적으로 스캔을 실행하고 새로운 매수 신호가 나타나면 알림을 표시합니다.
"""
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from main import StockSignalSystem
import config


class StockMonitor:
    """주식 매수 신호 자동 모니터링 클래스"""
    
    def __init__(self, scan_interval_minutes: int = 60, save_history: bool = True):
        """
        Args:
            scan_interval_minutes: 스캔 간격 (분)
            save_history: 신호 히스토리 저장 여부
        """
        self.system = StockSignalSystem()
        self.scan_interval = scan_interval_minutes * 60  # 초로 변환
        self.save_history = save_history
        self.history_file = 'signal_history.json'
        self.previous_signals = self._load_history()
        self.running = False
    
    def _load_history(self) -> Dict[str, dict]:
        """이전 신호 히스토리 로드"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_history(self, signals: List[dict]):
        """신호 히스토리 저장"""
        if not self.save_history:
            return
        
        history = {}
        for signal in signals:
            symbol = signal['symbol']
            history[symbol] = {
                'level': signal['level'],
                'score': signal['score'],
                'price': signal['price'],
                'date': str(signal['date']),
                'last_seen': datetime.now().isoformat()
            }
        
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 히스토리 저장 실패: {str(e)}")
    
    def _get_new_signals(self, current_signals: List[dict]) -> List[dict]:
        """새로운 신호만 필터링"""
        new_signals = []
        
        for signal in current_signals:
            symbol = signal['symbol']
            level = signal['level']
            score = signal['score']
            
            # 이전 신호와 비교
            if symbol in self.previous_signals:
                prev = self.previous_signals[symbol]
                # 신호 레벨이 변경되었거나 점수가 크게 향상된 경우
                if (prev['level'] != level or 
                    (level in ['STRONG_BUY', 'BUY'] and prev['level'] not in ['STRONG_BUY', 'BUY']) or
                    (level == 'STRONG_BUY' and prev['level'] != 'STRONG_BUY')):
                    new_signals.append(signal)
            else:
                # 처음 발견된 신호
                new_signals.append(signal)
        
        return new_signals
    
    def _display_new_signals(self, new_signals: List[dict]):
        """새로운 신호 표시"""
        if not new_signals:
            return
        
        print(f"\n{'='*60}")
        print(f"🔔 새로운 매수 신호 발견! ({len(new_signals)}개)")
        print(f"⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        emoji_map = {
            'STRONG_BUY': '🟢',
            'BUY': '🔵',
            'WATCH': '🟡'
        }
        
        # 신호 레벨별로 정렬
        level_order = {'STRONG_BUY': 0, 'BUY': 1, 'WATCH': 2}
        new_signals.sort(key=lambda x: (level_order.get(x['level'], 99), -x['score']))
        
        for signal in new_signals:
            emoji = emoji_map.get(signal['level'], '⚪')
            level_name = config.SIGNAL_LEVELS[signal['level']]['name']
            symbol = signal['symbol']
            
            # 이전 신호와 비교 정보
            if symbol in self.previous_signals:
                prev = self.previous_signals[symbol]
                change = f"({prev['level']} → {signal['level']})"
            else:
                change = "(신규)"
            
            print(f"{emoji} {symbol:6s} | {level_name:8s} | 점수: {signal['score']:4.1f}/10 | 가격: ${signal['price']:8.2f} {change}")
        
        print(f"\n{'='*60}\n")
    
    def scan_once(self, symbols: List[str], timeframe: str = 'short_swing', 
                  max_workers: int = 20) -> List[dict]:
        """한 번 스캔 실행"""
        print(f"\n{'='*60}")
        print(f"🔍 스캔 시작: {len(symbols)}개 종목")
        print(f"⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        signals = self.system.scan_multiple_symbols(
            symbols, 
            timeframe, 
            max_workers=max_workers,
            show_progress=False  # 모니터링 모드에서는 진행 상황 숨김
        )
        
        # 새로운 신호만 필터링
        new_signals = self._get_new_signals(signals)
        
        # 새로운 신호 표시
        if new_signals:
            self._display_new_signals(new_signals)
        else:
            print(f"✅ 새로운 신호 없음 (총 {len(signals)}개 신호 유지)")
        
        # 히스토리 업데이트
        self._save_history(signals)
        self.previous_signals = {s['symbol']: {
            'level': s['level'],
            'score': s['score'],
            'price': s['price'],
            'date': str(s['date'])
        } for s in signals}
        
        return new_signals
    
    def start_monitoring(self, symbols: List[str], timeframe: str = 'short_swing',
                        max_workers: int = 20):
        """
        자동 모니터링 시작
        
        Args:
            symbols: 모니터링할 종목 리스트
            timeframe: 시간프레임
            max_workers: 동시 실행 스레드 수
        """
        self.running = True
        
        print("="*60)
        print("🤖 자동 모니터링 시스템 시작")
        print("="*60)
        print(f"📊 모니터링 종목 수: {len(symbols)}개")
        print(f"⏱️  스캔 간격: {self.scan_interval // 60}분")
        print(f"🔄 스레드 수: {max_workers}개")
        print(f"💾 히스토리 저장: {'활성화' if self.save_history else '비활성화'}")
        print("="*60)
        print("\n⚠️  종료하려면 Ctrl+C를 누르세요\n")
        
        scan_count = 0
        
        try:
            while self.running:
                scan_count += 1
                print(f"\n{'='*60}")
                print(f"📡 스캔 #{scan_count}")
                print(f"{'='*60}")
                
                # 스캔 실행
                new_signals = self.scan_once(symbols, timeframe, max_workers)
                
                # 다음 스캔까지 대기
                if self.running:
                    next_scan = datetime.now().timestamp() + self.scan_interval
                    next_scan_time = datetime.fromtimestamp(next_scan).strftime('%H:%M:%S')
                    print(f"\n⏳ 다음 스캔까지 대기 중... (다음 스캔: {next_scan_time})")
                    
                    # 대기 중에도 종료 가능하도록 짧은 간격으로 체크
                    waited = 0
                    while waited < self.scan_interval and self.running:
                        time.sleep(10)  # 10초마다 체크
                        waited += 10
                        if waited % 60 == 0:  # 1분마다 남은 시간 표시
                            remaining = (self.scan_interval - waited) // 60
                            print(f"   남은 시간: {remaining}분...", end='\r')
        
        except KeyboardInterrupt:
            print("\n\n⚠️  모니터링 중지 요청됨")
            self.stop()
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            self.stop()
    
    def stop(self):
        """모니터링 중지"""
        self.running = False
        print("\n✅ 모니터링 시스템 종료")
        print(f"📊 총 스캔 횟수: {len(self.previous_signals)}개 종목 모니터링됨")


def main():
    """모니터링 시스템 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description='주식 매수 신호 자동 모니터링')
    parser.add_argument('--interval', type=int, default=60, 
                       help='스캔 간격 (분, 기본값: 60)')
    parser.add_argument('--symbols', type=int, default=100,
                       help='모니터링할 종목 수 (기본값: 100)')
    parser.add_argument('--workers', type=int, default=20,
                       help='동시 실행 스레드 수 (기본값: 20)')
    parser.add_argument('--timeframe', type=str, default='short_swing',
                       choices=['day_trading', 'short_swing', 'long_swing'],
                       help='시간프레임 (기본값: short_swing)')
    parser.add_argument('--no-history', action='store_true',
                       help='히스토리 저장 비활성화')
    
    args = parser.parse_args()
    
    # 모니터 생성
    monitor = StockMonitor(
        scan_interval_minutes=args.interval,
        save_history=not args.no_history
    )
    
    # 모니터링할 종목 선택
    symbols = config.DEFAULT_SYMBOLS[:args.symbols]
    
    # 모니터링 시작
    monitor.start_monitoring(
        symbols=symbols,
        timeframe=args.timeframe,
        max_workers=args.workers
    )


if __name__ == "__main__":
    main()

