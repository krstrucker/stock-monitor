"""Flask 서버 및 스케줄러"""
import os
import sys
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

app = Flask(__name__)
scheduler = BackgroundScheduler()
monitor = None
db = Database()

# 종목 리스트 가져오기 (간단한 버전)
def get_all_symbols():
    """전체 종목 리스트 가져오기"""
    try:
        # NASDAQ과 NYSE의 주요 종목들
        # 실제로는 더 많은 종목이 필요하지만, 여기서는 샘플만 제공
        # 실제 구현 시 symbol_fetcher.py를 사용하거나 외부 API 사용
        
        # 임시로 빈 리스트 반환 (실제로는 약 7000개 종목 필요)
        # 사용자가 직접 종목 리스트를 제공하거나 파일에서 로드해야 함
        return []
    except:
        return []

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
    """스케줄된 스캔 실행"""
    try:
        print(f"\n{'='*50}")
        print(f"🔄 스케줄된 스캔 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # 종목 리스트 가져오기
        symbol_count_str = os.environ.get('MONITOR_SYMBOL_COUNT', '0')
        symbol_count = int(symbol_count_str) if symbol_count_str else 0
        
        # 종목 리스트 로드 (실제 구현 필요)
        all_symbols = get_all_symbols()
        
        if symbol_count == 0 or symbol_count >= len(all_symbols):
            symbols = all_symbols
            print(f"📊 전체 종목 스캔: {len(symbols)}개 종목")
        else:
            symbols = all_symbols[:symbol_count]
            print(f"📊 제한된 종목 스캔: {len(symbols)}개 종목 (전체: {len(all_symbols)}개)")
        
        # 특수 문자 필터링
        valid_symbols = [s for s in symbols if '^' not in s and '/' not in s and '$' not in s]
        symbols = valid_symbols
        
        # 스캔 실행
        new_signals = monitor.scan_once(
            symbols=symbols,
            timeframe=os.environ.get('MONITOR_TIMEFRAME', 'short_swing'),
            max_workers=int(os.environ.get('MONITOR_WORKERS', '20'))
        )
        
        # 7.5점 이상 신호만 필터링 (이중 체크)
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
        
        # 새로운 신호가 있으면 알림 전송
        if filtered_signals:
            message = format_signal_message(filtered_signals)
            success = send_notification(message)
            if success:
                print(f"✅ 텔레그램 알림 전송 완료: {len(filtered_signals)}개 신호")
            else:
                print(f"⚠️ 텔레그램 알림 전송 실패")
        
    except Exception as e:
        print(f"❌ 스케줄된 스캔 실행 중 오류: {str(e)}")

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

