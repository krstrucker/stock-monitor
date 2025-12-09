# Railway 빠른 배포 가이드

## Railway란?

- **24시간 항상 켜져 있는 클라우드 서버**
- 컴퓨터가 꺼져 있어도 작동
- 무료 크레딧 제공 (월 5달러)
- 매우 간단한 배포

## 배포 단계

### 1단계: GitHub 저장소 준비

1. **Git 초기화** (아직 안 했다면)
```powershell
cd "C:\Users\용\Desktop\us stock auto"
git init
git add .
git commit -m "Initial commit"
```

2. **GitHub 저장소 생성**
   - https://github.com 접속
   - "New repository" 클릭
   - 저장소 이름 입력 (예: `stock-monitor`)
   - "Create repository" 클릭

3. **코드 푸시**
```powershell
git remote add origin https://github.com/your-username/stock-monitor.git
git branch -M main
git push -u origin main
```

### 2단계: Railway 계정 생성

1. https://railway.app 접속
2. "Login" 클릭
3. "Deploy from GitHub repo" 선택
4. GitHub 계정으로 로그인

### 3단계: 프로젝트 배포

1. **저장소 선택**
   - 방금 만든 GitHub 저장소 선택
   - "Deploy Now" 클릭

2. **자동 배포**
   - Railway가 자동으로 코드 감지
   - Python 프로젝트로 인식
   - 자동으로 배포 시작

### 4단계: 환경 변수 설정

Railway 대시보드에서:
1. 프로젝트 클릭
2. "Variables" 탭 클릭
3. 다음 환경 변수 추가:

```
TELEGRAM_BOT_TOKEN=8015894529:AAEINiwSRY58nwtEMFZWOCmjK1nmbu_pEBU
TELEGRAM_CHAT_ID=8130414883
MONITOR_SYMBOL_COUNT=0
MONITOR_WORKERS=20
MONITOR_TIMEFRAME=short_swing
PORT=5000
HOST=0.0.0.0
```

### 5단계: 완료!

1. **URL 확인**
   - Railway 대시보드에서 "Settings" 탭
   - "Generate Domain" 클릭
   - 생성된 URL 확인 (예: `https://your-app.railway.app`)

2. **서버 상태 확인**
   - `https://your-app.railway.app/status` 접속
   - 서버가 정상 작동하는지 확인

## 장점

✅ **24시간 항상 켜져 있음**
- 컴퓨터가 꺼져 있어도 작동
- 새벽 스캔도 자동 실행

✅ **자동 배포**
- GitHub에 푸시하면 자동 배포
- 코드 수정이 쉬움

✅ **무료 크레딧**
- 월 5달러 크레딧 제공
- 충분히 사용 가능

✅ **간단한 설정**
- 복잡한 설정 불필요
- 몇 번의 클릭으로 완료

## 주의사항

⚠️ **종목 리스트 필요**
- `symbol_fetcher.py`를 실제로 구현해야 함
- 또는 종목 리스트 파일 필요

⚠️ **무료 크레딧 한도**
- 월 5달러 크레딧
- 초과 시 유료 결제 필요 (하지만 충분함)

## 문제 해결

### 서버가 시작되지 않을 때
1. Railway 로그 확인
2. 환경 변수 확인
3. `requirements.txt` 확인

### 스케줄러가 작동하지 않을 때
1. 서버 로그에서 스케줄러 시작 확인
2. 시간대 설정 확인 (Asia/Seoul)

## 완료!

이제 **컴퓨터가 꺼져 있어도 서버가 작동합니다!** 🎉

- 24시간 항상 켜져 있음
- 새벽 스캔 자동 실행
- 텔레그램 알림 정상 작동
- 대시보드 어디서나 접속 가능

