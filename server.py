"""Flask 서버 및 스케줄러"""
import os
import sys
import warnings
import logging
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import config
from monitor import StockMonitor
from database import Database
from stock_info import get_stock_info, get_recommendation_reason, get_recent_news, get_pros_cons
from data_fetcher import fetch_stock_data
import requests
import json

# 모든 경고 및 yfinance 로그 억제
warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.CRITICAL)
os.environ['YFINANCE_DISABLE_WARNINGS'] = '1'

app = Flask(__name__)
scheduler = BackgroundScheduler()
monitor = None
db = Database()

# 종목 리스트 가져오기
from symbol_fetcher import get_all_symbols as fetch_symbols, get_symbols_from_file, save_symbols_to_file

def get_all_symbols():
    """전체 종목 리스트 가져오기"""
    try:
        # 파일에서 먼저 시도
        symbols = get_symbols_from_file('symbols.txt')
        if symbols and len(symbols) > 100:
            print(f"📁 파일에서 종목 리스트 로드: {len(symbols)}개")
            return symbols
        
        # 파일이 없거나 적으면 API에서 가져오기
        symbols = fetch_symbols()
        
        # 가져온 종목을 파일로 저장 (다음번에는 파일에서 로드)
        if symbols and len(symbols) > 100:
            save_symbols_to_file(symbols, 'symbols.txt')
        
        return symbols if symbols else []
    except Exception as e:
        print(f"❌ 종목 리스트 가져오기 오류: {str(e)}")
        # 최소한의 종목이라도 반환
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']

def send_notification(message):
    """텔레그램 알림 전송"""
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': config.TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def format_signal_message(signals):
    """신호 메시지 포맷팅"""
    message = "🔔 <b>새로운 매수 신호 발견!</b>\n\n"
    for signal in signals[:10]:  # 최대 10개만
        message += f"📈 {signal['symbol']}\n"
        message += f"   점수: {signal['score']}/10\n"
        message += f"   가격: ${signal['price']:.2f}\n"
        message += f"   레벨: {signal['level']}\n\n"
    
    if len(signals) > 10:
        message += f"... 외 {len(signals) - 10}개 더\n"
    
    return message

def init_scheduler():
    """스케줄러 초기화"""
    global monitor
    
    # StockMonitor 초기화
    monitor = StockMonitor(scan_interval_minutes=240, save_history=True)
    
    # 하루 2번 스캔: 22:30 (미국 시장 개장 시)와 02:30 (4시간 후)
    scheduler.add_job(
        scheduled_scan,
        CronTrigger(hour=22, minute=30, timezone='Asia/Seoul'),
        id='scan_morning',
        replace_existing=True
    )
    
    scheduler.add_job(
        scheduled_scan,
        CronTrigger(hour=2, minute=30, timezone='Asia/Seoul'),
        id='scan_afternoon',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ 스케줄러 시작됨: 매일 22:30, 02:30에 자동 스캔")

def scheduled_scan():
    """스케줄된 스캔 실행 (스케줄러용 - 실시간 업데이트 사용)"""
    scheduled_scan_with_realtime()

@app.route('/')
def index():
    """메인 페이지 (대시보드)"""
    try:
        with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"대시보드 파일을 불러올 수 없습니다: {str(e)}", 500

@app.route('/status')
def status():
    """서버 상태 확인"""
    symbol_count_str = os.environ.get('MONITOR_SYMBOL_COUNT', '0')
    symbol_count = int(symbol_count_str) if symbol_count_str else 0
    all_symbols = get_all_symbols()
    if symbol_count == 0:
        symbol_count = len(all_symbols)
    
    return jsonify({
        'status': 'running',
        'scheduler_running': scheduler.running,
        'monitor_active': monitor is not None,
        'interval_minutes': int(os.environ.get('MONITOR_INTERVAL', '60')),
        'symbol_count': symbol_count,
        'is_full_scan': symbol_count_str == '0' or symbol_count_str == '',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/signals')
def get_signals():
    """현재 신호 목록 조회"""
    if not monitor or not hasattr(monitor, 'previous_signals'):
        return jsonify({'signals': [], 'count': 0})
    
    signals = []
    for symbol, data in monitor.previous_signals.items():
        if data.get('score', 0) >= 7.5:  # 7.5점 이상만
            signals.append({
                'symbol': symbol,
                'level': data.get('level'),
                'score': data.get('score'),
                'price': data.get('price'),
                'last_seen': data.get('last_seen', data.get('date'))
            })
    
    return jsonify({
        'signals': signals,
        'count': len(signals),
        'timestamp': datetime.now().isoformat()
    })

# 스캔 진행 상태 저장
scan_status = {
    'is_scanning': False,
    'progress': 0,
    'total': 0,
    'found_signals': [],
    'start_time': None
}

@app.route('/scan', methods=['POST', 'GET'])
def trigger_scan():
    """즉시 스캔 실행 (비동기)"""
    global scan_status
    
    if scan_status['is_scanning']:
        return jsonify({
            'status': 'running',
            'message': '이미 스캔이 진행 중입니다.',
            'progress': scan_status['progress'],
            'total': scan_status['total'],
            'timestamp': datetime.now().isoformat()
        })
    
    # 비동기로 스캔 시작
    import threading
    thread = threading.Thread(target=scheduled_scan_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': '스캔이 시작되었습니다.',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/scan/status')
def get_scan_status():
    """스캔 진행 상태 조회"""
    return jsonify({
        'is_scanning': scan_status['is_scanning'],
        'progress': scan_status['progress'],
        'total': scan_status['total'],
        'found_count': len(scan_status['found_signals']),
        'start_time': scan_status['start_time'],
        'timestamp': datetime.now().isoformat()
    })

def scheduled_scan_async():
    """비동기 스캔 실행 (웹에서 즉시 스캔 버튼 클릭 시)"""
    global scan_status
    
    try:
        scan_status['is_scanning'] = True
        scan_status['progress'] = 0
        scan_status['found_signals'] = []
        scan_status['start_time'] = datetime.now().isoformat()
        
        scheduled_scan_with_realtime()
        
    finally:
        scan_status['is_scanning'] = False
        scan_status['progress'] = scan_status['total']  # 완료 표시

def scheduled_scan_with_realtime():
    """실시간 업데이트가 있는 스캔"""
    global scan_status
    
    # 스캔 상태 초기화 (스케줄러에서 직접 호출될 때도 설정)
    if not scan_status.get('is_scanning', False):
        scan_status['is_scanning'] = True
        scan_status['progress'] = 0
        scan_status['found_signals'] = []
        scan_status['start_time'] = datetime.now().isoformat()
    
    try:
        print(f"\n{'='*50}")
        print(f"🔄 스캔 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # 종목 리스트 가져오기
        symbol_count_str = os.environ.get('MONITOR_SYMBOL_COUNT', '0')
        symbol_count = int(symbol_count_str) if symbol_count_str else 0
        
        all_symbols = get_all_symbols()
        
        if symbol_count == 0 or symbol_count >= len(all_symbols):
            symbols = all_symbols
            print(f"📊 전체 종목 스캔: {len(symbols)}개 종목")
        else:
            symbols = all_symbols[:symbol_count]
            print(f"📊 제한된 종목 스캔: {len(symbols)}개 종목 (전체: {len(all_symbols)}개)")
        
        # 특수 문자 및 우선주 필터링 (symbol_fetcher에서 이미 필터링되었지만 이중 체크)
        valid_symbols = []
        for s in symbols:
            s_upper = s.upper().strip()
            # 우선주 제외
            if ('.PR' in s_upper or s_upper.endswith('-P') or 
                any(s_upper.endswith(f'-{chr(i)}') for i in range(65, 91))):  # -A ~ -Z
                continue
            # 특수 문자 제외
            if '^' not in s_upper and '/' not in s_upper and '$' not in s_upper:
                valid_symbols.append(s_upper)
        
        symbols = valid_symbols
        print(f"📊 최종 스캔 대상: {len(symbols)}개 종목 (우선주/상장폐지 제외)")
        
        scan_status['total'] = len(symbols)
        scan_status['progress'] = 0
        
        # monitor 객체 확인
        if monitor is None:
            print("❌ 오류: monitor 객체가 초기화되지 않았습니다. 초기화 중...")
            global monitor
            monitor = StockMonitor(scan_interval_minutes=240, save_history=True)
            print("✅ monitor 객체 초기화 완료")
        
        # 스캔 실행 전 즉시 진행률 출력
        print(f"⏳ 스캔 준비 완료, 시작합니다...")
        print(f"🔧 설정: workers={int(os.environ.get('MONITOR_WORKERS', '20'))}, timeframe={os.environ.get('MONITOR_TIMEFRAME', 'short_swing')}")
        
        try:
            # 스캔 실행 (실시간 업데이트 포함)
            new_signals = monitor.scan_once_with_realtime(
                symbols=symbols,
                timeframe=os.environ.get('MONITOR_TIMEFRAME', 'short_swing'),
                max_workers=int(os.environ.get('MONITOR_WORKERS', '20')),
                progress_callback=update_scan_progress
            )
        except Exception as scan_error:
            print(f"❌ 스캔 실행 중 오류 발생: {str(scan_error)}")
            import traceback
            traceback.print_exc()
            new_signals = []
        
        # 7.5점 이상 신호만 필터링
        min_score = 7.5
        filtered_signals = [s for s in new_signals if s.get('score', 0) >= min_score]
        
        if filtered_signals:
            print(f"✅ {min_score}점 이상 신호: {len(filtered_signals)}개 (새로운 신호)")
        else:
            print(f"⚠️ {min_score}점 이상 신호 없음")
        
        # 스캔 결과 데이터베이스에 저장
        all_qualified_signals = []
        if monitor and hasattr(monitor, 'previous_signals'):
            for symbol, data in monitor.previous_signals.items():
                if data.get('score', 0) >= min_score:
                    all_qualified_signals.append({
                        'symbol': symbol,
                        'level': data.get('level'),
                        'score': data.get('score'),
                        'price': data.get('price'),
                        'date': data.get('date', datetime.now().isoformat())
                    })
        
        if all_qualified_signals:
            try:
                db.save_scan(all_qualified_signals)
                print(f"✅ 스캔 결과 저장 완료: {len(all_qualified_signals)}개 신호 (7.5점 이상)")
            except Exception as e:
                print(f"⚠️ 스캔 결과 저장 실패: {str(e)}")
        
        # 전체 스캔 완료 후에만 텔레그램 알림 전송
        if filtered_signals:
            message = format_signal_message(filtered_signals)
            success = send_notification(message)
            if success:
                print(f"✅ 텔레그램 알림 전송 완료: {len(filtered_signals)}개 신호")
            else:
                print(f"⚠️ 텔레그램 알림 전송 실패")
        
    except Exception as e:
        print(f"❌ 스캔 실행 중 오류: {str(e)}")
    finally:
        scan_status['is_scanning'] = False

def update_scan_progress(completed, total, new_signal):
    """스캔 진행 상황 업데이트"""
    global scan_status
    scan_status['progress'] = completed
    
    # 새로운 신호 발견 시 실시간으로 추가 (7.5점 이상만)
    if new_signal and new_signal.get('score', 0) >= 7.5:
        # 중복 체크
        existing = next((s for s in scan_status['found_signals'] if s['symbol'] == new_signal['symbol']), None)
        if not existing:
            scan_status['found_signals'].append(new_signal)
            # 웹에서 즉시 볼 수 있도록 모니터에도 저장
            if monitor and hasattr(monitor, 'previous_signals'):
                monitor.previous_signals[new_signal['symbol']] = new_signal
                print(f"🟢 실시간 신호 발견: {new_signal['symbol']} ({new_signal['score']}점) - 웹에서 확인 가능")

@app.route('/scans')
def get_scans():
    """과거 스캔 결과 조회"""
    date = request.args.get('date')
    limit = int(request.args.get('limit', 50))
    
    if date:
        scans = db.get_scans_by_date(date)
    else:
        scans = db.get_all_scans(limit)
    
    return jsonify({
        'scans': scans,
        'count': len(scans),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/symbol/<symbol>')
def get_symbol_detail(symbol):
    """종목 상세 정보"""
    try:
        if not monitor or not hasattr(monitor, 'previous_signals'):
            return jsonify({'error': '모니터가 초기화되지 않았습니다'}), 500
        
        signal_data = monitor.previous_signals.get(symbol)
        if not signal_data:
            return jsonify({'error': '종목을 찾을 수 없습니다'}), 404
        
        stock_info = get_stock_info(symbol)
        reason = get_recommendation_reason(symbol, signal_data)
        news = get_recent_news(symbol, limit=5)
        pros_cons = get_pros_cons(symbol, signal_data)
        
        return jsonify({
            'symbol': symbol,
            'stock_info': stock_info,
            'signal': signal_data,
            'recommendation_reason': reason,
            'news': news,
            'pros_cons': pros_cons
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chart/<symbol>')
def get_chart_data(symbol):
    """차트 데이터"""
    try:
        data = fetch_stock_data(symbol, period='6mo')
        if data is None or data.empty:
            return jsonify({'error': '데이터를 가져올 수 없습니다'}), 404
        
        # 캔들 데이터
        candles = []
        for idx, row in data.iterrows():
            candles.append({
                'time': int(idx.timestamp()),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close'])
            })
        
        # 신호 마커
        markers = []
        if monitor and hasattr(monitor, 'previous_signals'):
            signal_data = monitor.previous_signals.get(symbol)
            if signal_data:
                signal_date = datetime.fromisoformat(signal_data.get('date', '').replace('Z', '+00:00'))
                if signal_date:
                    markers.append({
                        'time': int(signal_date.timestamp()),
                        'position': 'belowBar',
                        'color': '#2196F3',
                        'shape': 'arrowUp',
                        'text': f"신호: {signal_data.get('score', 0)}점"
                    })
        
        return jsonify({
            'candles': candles,
            'markers': markers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/top-performers')
def get_top_performers():
    """주간/월간 TOP 10"""
    period = request.args.get('period', 'week')  # 'week' or 'month'
    
    try:
        performers = db.get_top_performers(period=period, limit=10)
        return jsonify({
            'period': period,
            'performers': performers,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 환경 변수 설정 확인
    print("="*50)
    print("주식 매수 신호 모니터링 서버")
    print("="*50)
    
    # 스케줄러 초기화
    init_scheduler()
    
    # 서버 시작
    # Railway나 다른 클라우드 서비스에서는 PORT 환경 변수를 사용
    port = int(os.environ.get('PORT', config.PORT))
    host = os.environ.get('HOST', config.HOST)
    
    symbol_count_str = os.environ.get('MONITOR_SYMBOL_COUNT', '0')
    symbol_count = int(symbol_count_str) if symbol_count_str else 0
    all_symbols = get_all_symbols()
    if symbol_count == 0:
        symbol_count = len(all_symbols) if all_symbols else 0
    
    print(f"\n서버 시작: http://{host}:{port}")
    print(f"모니터링 종목 수: {symbol_count}개")
    print(f"스케줄: 매일 22:30, 02:30 (KST)")
    print(f"최소 점수: 7.5점 이상\n")
    
    try:
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        print("\n서버 종료 중...")
        scheduler.shutdown()
        sys.exit(0)

