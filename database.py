"""데이터베이스 관리"""
import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path='scans.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 스캔 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date TEXT NOT NULL,
                signal_count INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 신호 히스토리 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                symbol TEXT NOT NULL,
                level TEXT,
                score REAL,
                price REAL,
                signal_date TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(id)
            )
        ''')
        
        # 성과 추적 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                buy_date TEXT,
                buy_price REAL,
                sell_date TEXT,
                sell_price REAL,
                return_rate REAL
            )
        ''')
        
        # 일일 가격 추적 테이블 (수익률 계산용)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price_date DATE NOT NULL,
                price REAL NOT NULL,
                score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, price_date)
            )
        ''')
        
        # 인덱스 추가 (조회 성능 향상)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_daily_prices_symbol_date 
            ON daily_prices(symbol, price_date DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_signal_history_symbol 
            ON signal_history(symbol)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_scan(self, signals):
        """스캔 결과 저장 및 일일 가격 저장"""
        if not signals:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        price_date = datetime.now().strftime('%Y-%m-%d')  # 날짜만 (일일 가격용)
        
        # 스캔 기록
        cursor.execute('''
            INSERT INTO scans (scan_date, signal_count)
            VALUES (?, ?)
        ''', (scan_date, len(signals)))
        
        scan_id = cursor.lastrowid
        
        # 신호 저장 및 일일 가격 저장
        for signal in signals:
            symbol = signal.get('symbol')
            price = signal.get('price', 0)
            score = signal.get('score', 0)
            
            # 신호 히스토리 저장
            cursor.execute('''
                INSERT INTO signal_history (scan_id, symbol, level, score, price, signal_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                symbol,
                signal.get('level'),
                score,
                price,
                signal.get('date', scan_date)
            ))
            
            # 일일 가격 저장 (중복 시 업데이트)
            cursor.execute('''
                INSERT OR REPLACE INTO daily_prices (symbol, price_date, price, score)
                VALUES (?, ?, ?, ?)
            ''', (symbol, price_date, price, score))
        
        conn.commit()
        conn.close()
    
    def get_all_scans(self, limit=50):
        """모든 스캔 결과 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, s.scan_date, s.signal_count,
                   GROUP_CONCAT(sh.symbol || ':' || sh.score) as signals
            FROM scans s
            LEFT JOIN signal_history sh ON s.id = sh.scan_id
            GROUP BY s.id
            ORDER BY s.scan_date DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        scans = []
        for row in results:
            scans.append({
                'id': row[0],
                'scan_date': row[1],
                'signal_count': row[2],
                'signals': row[3] if row[3] else ''
            })
        
        return scans
    
    def get_scans_by_date(self, date):
        """특정 날짜의 스캔 결과 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, s.scan_date, s.signal_count,
                   sh.symbol, sh.level, sh.score, sh.price
            FROM scans s
            LEFT JOIN signal_history sh ON s.id = sh.scan_id
            WHERE DATE(s.scan_date) = DATE(?)
            ORDER BY sh.score DESC
        ''', (date,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_symbol_history(self, symbol):
        """특정 종목의 히스토리 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT scan_date, level, score, price
            FROM signal_history sh
            JOIN scans s ON sh.scan_id = s.id
            WHERE sh.symbol = ?
            ORDER BY s.scan_date DESC
        ''', (symbol,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_top_performers(self, period='week', limit=10):
        """주간/월간 수익률 TOP 10 (실제 수익률 기준)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if period == 'week':
            days_back = 7
        else:  # month
            days_back = 30
        
        # 각 종목의 첫 가격과 현재 가격을 비교하여 수익률 계산
        cursor.execute('''
            WITH first_prices AS (
                SELECT 
                    symbol,
                    price as first_price,
                    price_date as first_date
                FROM daily_prices
                WHERE price_date >= date('now', '-' || ? || ' days')
                GROUP BY symbol
                HAVING MIN(price_date)
            ),
            latest_prices AS (
                SELECT 
                    symbol,
                    price as latest_price,
                    price_date as latest_date
                FROM daily_prices
                WHERE price_date >= date('now', '-' || ? || ' days')
                GROUP BY symbol
                HAVING MAX(price_date)
            ),
            avg_scores AS (
                SELECT 
                    symbol,
                    AVG(score) as avg_score,
                    COUNT(*) as signal_count
                FROM signal_history sh
                JOIN scans s ON sh.scan_id = s.id
                WHERE s.scan_date >= datetime('now', '-' || ? || ' days')
                GROUP BY symbol
            )
            SELECT 
                fp.symbol,
                fp.first_price,
                lp.latest_price,
                CASE 
                    WHEN fp.first_price > 0 
                    THEN ((lp.latest_price - fp.first_price) / fp.first_price * 100)
                    ELSE 0
                END as return_rate,
                COALESCE(avg.avg_score, 0) as avg_score,
                COALESCE(avg.signal_count, 0) as signal_count
            FROM first_prices fp
            JOIN latest_prices lp ON fp.symbol = lp.symbol
            LEFT JOIN avg_scores avg ON fp.symbol = avg.symbol
            WHERE fp.first_price > 0 AND lp.latest_price > 0
            ORDER BY return_rate DESC
            LIMIT ?
        ''', (days_back, days_back, days_back, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        performers = []
        for row in results:
            performers.append({
                'symbol': row[0],
                'first_price': round(row[1], 2),
                'latest_price': round(row[2], 2),
                'return_rate': round(row[3], 2),
                'avg_score': round(row[4], 2),
                'signal_count': row[5]
            })
        
        return performers
    
    def get_latest_signals(self, limit=100):
        """최근 신호 가져오기 (서버 재시작 시 복원용)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT sh.symbol, sh.level, sh.score, sh.price, sh.signal_date,
                   sh.symbol as symbol_key
            FROM signal_history sh
            JOIN scans s ON sh.scan_id = s.id
            WHERE sh.score >= 6.5
            ORDER BY s.scan_date DESC, sh.score DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        signals = {}
        for row in results:
            symbol = row[0]
            if symbol not in signals:  # 가장 최근 것만 저장
                signals[symbol] = {
                    'symbol': symbol,
                    'level': row[1] or 'WATCH',
                    'score': row[2] or 0,
                    'total_score': row[2] or 0,
                    'price': row[3] or 0,
                    'date': row[4] or datetime.now().isoformat(),
                    'last_seen': row[4] or datetime.now().isoformat()
                }
        
        return signals

