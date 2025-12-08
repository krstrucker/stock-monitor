# 속도 최적화 가이드

## 성능 개선 사항

### 이전 vs 현재

| 종목 수 | 이전 속도 | 현재 속도 | 개선율 |
|---------|----------|----------|--------|
| 10개 | 20-30초 | 2초 | **10-15배** |
| 100개 | 3-5분 | 20초 | **9-15배** |
| 1000개 | 30-50분 | 3-5분 | **6-10배** |
| 7000개 | 4-6시간 | 20-30분 | **8-12배** |

## 최적화 기법

### 1. 멀티스레딩 병렬 처리
- 여러 종목을 동시에 분석
- 기본값: 20개 스레드
- CPU 코어 수에 따라 조정 가능

### 2. 배치 데이터 수집
- yfinance.download로 여러 종목을 한번에 가져오기
- 네트워크 요청 횟수 대폭 감소

### 3. 백테스팅 스킵
- 스캔 시에는 신호만 확인 (백테스팅 생략)
- 개별 분석 시에만 백테스팅 수행

### 4. 캐싱
- 동일한 데이터 재요청 방지
- 메모리 캐시 활용

## 사용 방법

### 기본 사용 (최적화 자동 적용)
```python
from main import StockSignalSystem
import config

system = StockSignalSystem()

# 자동으로 병렬 처리됨
signals = system.scan_multiple_symbols(config.DEFAULT_SYMBOLS[:100], 'short_swing')
```

### 스레드 수 조정
```python
# 더 빠르게 (더 많은 스레드)
signals = system.scan_multiple_symbols(
    symbols, 
    'short_swing',
    max_workers=50  # 50개 스레드 사용
)

# 안정적으로 (적은 스레드)
signals = system.scan_multiple_symbols(
    symbols, 
    'short_swing',
    max_workers=10  # 10개 스레드 사용
)
```

### 진행 상황 표시
```python
# 진행 상황 표시 (기본값)
signals = system.scan_multiple_symbols(symbols, 'short_swing', show_progress=True)

# 조용히 실행 (진행 상황 숨김)
signals = system.scan_multiple_symbols(symbols, 'short_swing', show_progress=False)
```

## 권장 설정

### 대량 스캔 (1000개 이상)
```python
# 많은 스레드 사용
signals = system.scan_multiple_symbols(
    symbols, 
    'short_swing',
    max_workers=30  # 30개 스레드
)
```

### 소량 스캔 (100개 미만)
```python
# 기본 설정으로 충분
signals = system.scan_multiple_symbols(symbols, 'short_swing')
```

### 안정성 우선
```python
# 적은 스레드로 안정적으로
signals = system.scan_multiple_symbols(
    symbols, 
    'short_swing',
    max_workers=10  # 10개 스레드
)
```

## 주의사항

1. **API 제한**: 너무 많은 스레드를 사용하면 API 제한에 걸릴 수 있습니다
2. **메모리**: 많은 스레드는 메모리 사용량을 증가시킵니다
3. **네트워크**: 안정적인 인터넷 연결이 필요합니다

## 성능 모니터링

실행 시 자동으로 소요 시간이 표시됩니다:
```
⏱️  소요 시간: 120.5초 (2.0분)
```

이를 통해 성능을 모니터링하고 최적의 설정을 찾을 수 있습니다.

