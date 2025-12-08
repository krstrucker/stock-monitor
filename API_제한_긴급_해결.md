# API 제한 긴급 해결 방법

## 현재 문제

로그에서 확인된 문제:
1. **API 제한 발생**: `YFRateLimitError('Too Many Requests. Rate limited. Try after a while.')`
2. **Heroku 타임아웃**: `H20 desc="App boot timeout"`
3. **서버 크래시**: `State changed from starting to crashed`

## 즉시 해결 방법

### 1. 스레드 수 더 줄이기 (가장 중요!)

```powershell
heroku config:set MONITOR_WORKERS=10 --app your-stock-monitor
```

### 2. 특수 문자 종목 필터링 (자동 적용됨)

코드가 자동으로 다음 종목들을 제외합니다:
- `^` 포함 종목 (예: `BCV^A`, `BEP^A`)
- `/` 포함 종목 (예: `BF/A`, `BRK/B`)
- `$` 포함 종목

### 3. 요청 간격 늘리기 (자동 적용됨)

- 각 요청 사이 0.5-1초 대기
- API 제한 감지 시 최대 60초 대기

### 4. Heroku 타임아웃 해결

Procfile을 gunicorn으로 변경했습니다:
```
web: gunicorn --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --threads 1 server:app
```

## 권장 설정 (7000개 종목)

```powershell
# 스레드 수 줄이기 (API 제한 회피)
heroku config:set MONITOR_WORKERS=10 --app your-stock-monitor

# 종목 수는 그대로 유지
heroku config:set MONITOR_SYMBOL_COUNT=7000 --app your-stock-monitor

# 스캔 간격 늘리기
heroku config:set MONITOR_INTERVAL=240 --app your-stock-monitor
```

## 변경 사항 재배포

코드를 수정했으므로 재배포가 필요합니다:

```powershell
git add .
git commit -m "API 제한 대응 및 특수 문자 종목 필터링"
git push heroku master
```

## 완료 후 확인

```powershell
heroku logs --tail --app your-stock-monitor
```

API 제한 에러가 줄어들고 서버가 정상적으로 실행되는지 확인하세요.

