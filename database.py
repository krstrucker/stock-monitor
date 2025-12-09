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
        
        conn.commit()
        conn.close()
    
    def save_scan(self, signals):
        """스캔 결과 저장"""
        if not signals:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 스캔 기록
        cursor.execute('''
            INSERT INTO scans (scan_date, signal_count)
            VALUES (?, ?)
        ''', (scan_date, len(signals)))
        
        scan_id = cursor.lastrowid
        
        # 신호 저장
        for signal in signals:
            cursor.execute('''
                INSERT INTO signal_history (scan_id, symbol, level, score, price, signal_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                signal.get('symbol'),
                signal.get('level'),
                signal.get('score'),
                signal.get('price'),
                signal.get('date', scan_date)
            ))
        
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
        """주간/월간 수익률 TOP 10"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if period == 'week':
            date_filter = "datetime('now', '-7 days')"
        else:  # month
            date_filter = "datetime('now', '-30 days')"
        
        cursor.execute(f'''
            SELECT symbol, AVG(score) as avg_score, COUNT(*) as signal_count
            FROM signal_history sh
            JOIN scans s ON sh.scan_id = s.id
            WHERE s.scan_date >= {date_filter}
            GROUP BY symbol
            ORDER BY avg_score DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        performers = []
        for row in results:
            performers.append({
                'symbol': row[0],
                'avg_score': round(row[1], 2),
                'signal_count': row[2]
            })
        
        return performers

