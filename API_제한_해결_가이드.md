# API 제한 해결 가이드

## API 제한이 걸리면?

yfinance API 제한에 걸리면 다음과 같은 증상이 나타납니다:
- `HTTP Error 429: Too Many Requests`
- `HTTP Error 403: Forbidden`
- 데이터를 가져오지 못함
- 일부 종목만 스캔되고 나머지는 실패

## 해결 방법

### 방법 1: 스레드 수 줄이기 (가장 효과적)

동시 요청 수를 줄여서 API 제한을 피합니다.

```powershell
# 스레드 수 줄이기
heroku config:set MONITOR_WORKERS=10 --app your-stock-monitor
```

**권장 설정:**
- 7000개 종목: 15-20개 스레드
- 1000개 종목: 20-25개 스레드
- 100개 종목: 25-30개 스레드

### 방법 2: 요청 간격 늘리기 (Rate Limiting)

요청 사이에 대기 시간을 추가합니다.

**코드 수정 필요:**
- `data_fetcher.py`에 요청 간격 추가
- 각 요청 사이에 0.1-0.5초 대기

### 방법 3: 재시도 로직 활용 (자동)

이미 구현된 재시도 로직이 자동으로 작동합니다:
- 실패 시 자동으로 재시도
- 최대 3회 재시도
- 재시도 간격: 1초

### 방법 4: 스캔 간격 늘리기

스캔을 덜 자주 실행하여 API 호출을 줄입니다.

```powershell
# 3시간마다 스캔 (기본 60분)
heroku config:set MONITOR_INTERVAL=180 --app your-stock-monitor
```

### 방법 5: 배치 처리

종목을 여러 배치로 나누어 처리합니다.

**장점:**
- API 제한 회피
- 메모리 사용량 감소
- 오류 발생 시 일부만 영향

### 방법 6: 캐싱 활용

이미 가져온 데이터를 재사용합니다.

**현재 구현:**
- `DataFetcher` 클래스에 캐싱 기능 있음
- 동일한 종목/기간 데이터는 재사용

## 즉시 해결 방법

### 1. 스레드 수 줄이기
```powershell
heroku config:set MONITOR_WORKERS=15 --app your-stock-monitor
```

### 2. 서버 재시작
```powershell
heroku restart --app your-stock-monitor
```

### 3. 로그 확인
```powershell
heroku logs --tail --app your-stock-monitor
```

## 예방 방법

### 권장 설정 (7000개 종목)
```powershell
heroku config:set MONITOR_WORKERS=15 --app your-stock-monitor
heroku config:set MONITOR_INTERVAL=180 --app your-stock-monitor
heroku config:set MONITOR_SYMBOL_COUNT=7000 --app your-stock-monitor
```

이 설정으로:
- API 제한 회피
- 안정적인 스캔
- 느리지만 확실함

## API 제한 발생 시 대응

1. **로그 확인**: 어떤 종목에서 실패했는지 확인
2. **스레드 수 줄이기**: 15개 이하로 조정
3. **서버 재시작**: 설정 변경 후 재시작
4. **잠시 대기**: API 제한이 해제될 때까지 대기 (보통 몇 분)

## 완료!

이 방법들로 API 제한 문제를 해결할 수 있습니다!

