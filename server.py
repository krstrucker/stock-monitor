"""
주식 매수 신호 모니터링 서버
Flask 기반 웹 서버로 백그라운드에서 모니터링하고 카카오톡으로 알림을 보냅니다.
"""
from flask import Flask, jsonify, render_template_string
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import os
import json
from datetime import datetime
from monitor import StockMonitor
from kakao_notifier import TelegramNotifier
import config

app = Flask(__name__)
scheduler = BackgroundScheduler()
monitor = None

# 텔레그램 알림 설정
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# 텔레그램 알림 객체 초기화
telegram_notifier = TelegramNotifier() if (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID) else None


def send_notification(message: str):
    """
    텔레그램 알림 전송
    
    Args:
        message: 전송할 메시지
    
    Returns:
        전송 성공 여부
    """
    if not telegram_notifier:
        print("⚠️ 텔레그램 알림이 설정되지 않았습니다.")
        return False
    
    return telegram_notifier.send_message(message)


def format_signal_message(signals: list) -> str:
    """신호를 카카오톡 메시지 형식으로 포맷팅"""
    if not signals:
        return "새로운 매수 신호가 없습니다."
    
    emoji_map = {
        'STRONG_BUY': '🟢',
        'BUY': '🔵',
        'WATCH': '🟡'
    }
    
    message = f"🔔 새로운 매수 신호 발견! ({len(signals)}개)\n\n"
    
    for signal in signals[:10]:  # 최대 10개만 표시
        emoji = emoji_map.get(signal['level'], '⚪')
        level_name = config.SIGNAL_LEVELS[signal['level']]['name']
        message += f"{emoji} {signal['symbol']}: {level_name}\n"
        message += f"   점수: {signal['score']}/10\n"
        message += f"   가격: ${signal['price']}\n\n"
    
    if len(signals) > 10:
        message += f"... 외 {len(signals) - 10}개 더\n"
    
    message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return message


def scheduled_scan():
    """스케줄된 스캔 실행"""
    global monitor
    
    if not monitor:
        return
    
    try:
        print(f"\n{'='*60}")
        print(f"📡 스케줄된 스캔 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # 모니터링할 종목 수 (환경 변수에서 가져오기)
        symbol_count = int(os.environ.get('MONITOR_SYMBOL_COUNT', '100'))
        
        # 유효한 종목만 필터링 (특수 문자 제거)
        def is_valid_symbol(symbol):
            """유효한 종목 심볼인지 확인"""
            if not symbol or len(symbol) == 0:
                return False
            # 특수 문자가 포함된 종목 제외 (^, / 등은 대부분 상장폐지 또는 우선주)
            if '^' in symbol or '/' in symbol or '$' in symbol:
                return False
            # 너무 짧거나 긴 심볼 제외
            if len(symbol) < 1 or len(symbol) > 10:
                return False
            return True
        
        # 유효한 종목만 필터링
        valid_symbols = [s for s in config.DEFAULT_SYMBOLS if is_valid_symbol(s)]
        print(f"✅ 유효한 종목: {len(valid_symbols)}개 (전체: {len(config.DEFAULT_SYMBOLS)}개)")
        
        # 필터링 방법 선택
        filter_method = os.environ.get('FILTER_METHOD', 'none').lower()
        # 'none': 필터링 없음 (앞에서부터)
        # 'market_cap': 시가총액 기준
        # 'index_priority': 인덱스 우선순위 기준
        
        if filter_method == 'market_cap':
            from symbol_filter import filter_by_market_cap
            min_cap = os.environ.get('MIN_MARKET_CAP')
            min_cap = float(min_cap) if min_cap else None
            symbols = filter_by_market_cap(
                valid_symbols, 
                top_n=symbol_count,
                min_market_cap=min_cap,
                max_workers=int(os.environ.get('MONITOR_WORKERS', '20'))
            )
        elif filter_method == 'index_priority':
            from symbol_filter import filter_by_index_priority
            symbols = filter_by_index_priority(
                valid_symbols,
                top_n=symbol_count
            )
        else:
            # 기본: 앞에서부터 선택
            symbols = valid_symbols[:symbol_count]
        
        # 스캔 실행
        new_signals = monitor.scan_once(
            symbols=symbols,
            timeframe=os.environ.get('MONITOR_TIMEFRAME', 'short_swing'),
            max_workers=int(os.environ.get('MONITOR_WORKERS', '20'))
        )
        
        # 7.5점 이상 신호만 필터링 (고수익 전략)
        min_score = 7.5
        filtered_signals = [s for s in new_signals if s.get('score', 0) >= min_score]
        
        if filtered_signals:
            print(f"✅ {min_score}점 이상 신호: {len(filtered_signals)}개 (전체: {len(new_signals)}개)")
        elif new_signals:
            print(f"⚠️ {min_score}점 이상 신호 없음 (전체: {len(new_signals)}개)")
        
        # 새로운 신호가 있으면 알림 전송 (7.5점 이상만)
        if filtered_signals:
            message = format_signal_message(filtered_signals)
            send_notification(message)
        
    except Exception as e:
        print(f"❌ 스케줄된 스캔 실행 중 오류: {str(e)}")


@app.route('/')
def index():
    """메인 페이지"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>주식 매수 신호 모니터링 서버</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .status { padding: 15px; margin: 20px 0; border-radius: 5px; }
            .running { background: #d4edda; color: #155724; }
            .info { background: #d1ecf1; color: #0c5460; }
            button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 주식 매수 신호 모니터링 서버</h1>
            <div class="status running">
                ✅ 서버 실행 중
            </div>
            <div class="info">
                <h3>서버 정보</h3>
                <p>모니터링 간격: {{ interval }}분</p>
                <p>모니터링 종목 수: {{ symbol_count }}개</p>
                <p>마지막 스캔: {{ last_scan }}</p>
            </div>
            <div>
                <h3>API 엔드포인트</h3>
                <ul>
                    <li><a href="/status">/status</a> - 서버 상태</li>
                    <li><a href="/signals">/signals</a> - 현재 신호 목록</li>
                    <li><a href="/scan">/scan</a> - 즉시 스캔 실행</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    interval = int(os.environ.get('MONITOR_INTERVAL', '60'))
    symbol_count = int(os.environ.get('MONITOR_SYMBOL_COUNT', '100'))
    last_scan = "아직 실행되지 않음"
    
    if monitor and hasattr(monitor, 'previous_signals'):
        last_scan = f"{len(monitor.previous_signals)}개 종목 모니터링 중"
    
    return render_template_string(
        html,
        interval=interval,
        symbol_count=symbol_count,
        last_scan=last_scan
    )


@app.route('/status')
def status():
    """서버 상태 확인"""
    return jsonify({
        'status': 'running',
        'scheduler_running': scheduler.running,
        'monitor_active': monitor is not None,
        'interval_minutes': int(os.environ.get('MONITOR_INTERVAL', '60')),
        'symbol_count': int(os.environ.get('MONITOR_SYMBOL_COUNT', '100')),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/signals')
def get_signals():
    """현재 신호 목록 조회"""
    if not monitor or not hasattr(monitor, 'previous_signals'):
        return jsonify({'signals': [], 'count': 0})
    
    signals = []
    for symbol, data in monitor.previous_signals.items():
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


@app.route('/performance')
def get_performance():
    """전체 성과 통계 조회"""
    try:
        from performance_stats import PerformanceStats
        
        stats = PerformanceStats()
        
        # 현재 모니터링 중인 종목들
        if monitor and hasattr(monitor, 'previous_signals'):
            symbols = list(monitor.previous_signals.keys())
        else:
            symbol_count = int(os.environ.get('MONITOR_SYMBOL_COUNT', '100'))
            symbols = config.DEFAULT_SYMBOLS[:symbol_count]
        
        # 성과 통계 계산 (샘플링 - 전체는 시간이 오래 걸림)
        sample_size = min(100, len(symbols))  # 최대 100개만 샘플링
        sample_symbols = symbols[:sample_size]
        
        performance = stats.get_overall_statistics(sample_symbols, 'short_swing')
        
        return jsonify({
            'performance': performance,
            'sample_size': sample_size,
            'total_symbols': len(symbols),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/scan', methods=['POST', 'GET'])
def trigger_scan():
    """즉시 스캔 실행"""
    try:
        scheduled_scan()
        return jsonify({
            'status': 'success',
            'message': '스캔이 실행되었습니다.',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def init_scheduler():
    """스케줄러 초기화"""
    global monitor
    
    # 모니터 생성
    interval_minutes = int(os.environ.get('MONITOR_INTERVAL', '60'))
    monitor = StockMonitor(
        scan_interval_minutes=interval_minutes,
        save_history=True
    )
    
    # 스케줄러에 작업 추가
    scheduler.add_job(
        func=scheduled_scan,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id='stock_scan',
        name='주식 매수 신호 스캔',
        replace_existing=True
    )
    
    # 스케줄러 시작
    scheduler.start()
    print("✅ 스케줄러 시작됨")
    
    # 종료 시 스케줄러 정리
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    # 환경 변수 확인
    print("="*60)
    print("🚀 주식 매수 신호 모니터링 서버 시작")
    print("="*60)
    print(f"📊 모니터링 간격: {os.environ.get('MONITOR_INTERVAL', '60')}분")
    print(f"📈 모니터링 종목 수: {os.environ.get('MONITOR_SYMBOL_COUNT', '100')}개")
    print(f"🔄 스레드 수: {os.environ.get('MONITOR_WORKERS', '20')}개")
    
    # 텔레그램 알림 설정 확인
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        print("✅ 텔레그램 알림 설정됨")
    else:
        print("⚠️ 텔레그램 알림이 설정되지 않았습니다.")
        print("   환경 변수를 설정해주세요:")
        print("   - TELEGRAM_BOT_TOKEN")
        print("   - TELEGRAM_CHAT_ID")
    
    print("="*60)
    
    # 스케줄러 초기화
    init_scheduler()
    
    # 즉시 한 번 스캔 실행
    print("\n📡 초기 스캔 실행...")
    scheduled_scan()
    
    # Flask 서버 시작
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"\n🌐 웹 서버 시작: http://{host}:{port}")
    print("⚠️ 종료하려면 Ctrl+C를 누르세요\n")
    
    # Heroku에서는 gunicorn을 사용하므로 직접 실행하지 않음
    if os.environ.get('DYNO'):
        # Heroku 환경에서는 gunicorn이 실행하므로 여기서는 실행하지 않음
        print("✅ Heroku 환경 감지: gunicorn이 서버를 실행합니다.")
        # gunicorn이 실행하므로 여기서는 아무것도 하지 않음
    else:
        # 로컬 환경에서만 직접 실행
        app.run(host=host, port=port, debug=False)

