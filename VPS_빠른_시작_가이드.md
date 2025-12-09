# VPS 빠른 시작 가이드 (DigitalOcean)

## 5분 안에 시작하기

### 1단계: DigitalOcean 가입 (1분)
1. https://www.digitalocean.com 접속
2. "Sign Up" 클릭
3. 이메일로 가입

### 2단계: Droplet 생성 (2분)
1. "Create" → "Droplets" 클릭
2. **설정:**
   - Image: Ubuntu 22.04
   - Plan: Basic $4/mo (가장 저렴한 옵션)
   - Region: 가장 가까운 지역
   - Authentication: Password (간단함)
3. "Create Droplet" 클릭
4. **IP 주소 복사** (예: `123.45.67.89`)

### 3단계: SSH 접속 (1분)

**Windows PowerShell에서:**
```powershell
ssh root@123.45.67.89
```

비밀번호 입력 (이메일로 전송됨)

### 4단계: 서버 설정 (1분)

SSH 접속 후 다음 명령어 실행:

```bash
# 시스템 업데이트
apt update && apt upgrade -y

# 필수 패키지 설치
apt install python3 python3-pip git screen -y

# 프로젝트 클론 (GitHub에 업로드했다면)
git clone https://github.com/your-username/stock-monitor.git
cd stock-monitor

# 또는 파일 직접 업로드 (WinSCP 사용)
# WinSCP로 파일 업로드 후:
cd /root/stock-monitor

# 패키지 설치
pip3 install -r requirements.txt
```

### 5단계: 환경 변수 설정

```bash
# 환경 변수 파일 생성
nano .env
```

다음 내용 추가:
```
TELEGRAM_BOT_TOKEN=8015894529:AAEINiwSRY58nwtEMFZWOCmjK1nmbu_pEBU
TELEGRAM_CHAT_ID=8130414883
MONITOR_SYMBOL_COUNT=0
MONITOR_WORKERS=20
MONITOR_TIMEFRAME=short_swing
PORT=5000
HOST=0.0.0.0
```

저장: `Ctrl+X`, `Y`, `Enter`

### 6단계: 서버 실행

**간단한 방법 (screen 사용):**
```bash
# screen 세션 시작
screen -S stock-server

# 서버 실행
python3 server.py

# 세션 분리: Ctrl+A, D
# 나중에 다시 접속: screen -r stock-server
```

**또는 백그라운드 실행:**
```bash
nohup python3 server.py > server.log 2>&1 &
```

### 7단계: 방화벽 설정

```bash
ufw allow 22/tcp    # SSH
ufw allow 5000/tcp  # Flask 서버
ufw enable
```

### 완료!

- 서버 실행 중: `http://your-ip:5000`
- 상태 확인: `http://your-ip:5000/status`
- 로그 확인: `tail -f server.log`

## 유용한 명령어

```bash
# 서버 상태 확인
ps aux | grep python

# 서버 종료
pkill -f server.py

# 로그 확인
tail -f server.log

# screen 세션 목록
screen -ls

# screen 세션 접속
screen -r stock-server
```

## 문제 해결

### 서버가 실행되지 않을 때
```bash
# Python 경로 확인
which python3

# 패키지 확인
pip3 list

# 에러 로그 확인
python3 server.py
```

### 포트가 열리지 않을 때
```bash
# 포트 확인
netstat -tulpn | grep 5000

# 방화벽 확인
ufw status
```

## 비용

- **DigitalOcean**: 월 $4 (가장 저렴)
- **Vultr**: 월 $2.5 (더 저렴하지만 설정 복잡)
- **AWS EC2**: 월 $3.5~ (무료 티어 있음)

## 다음 단계

1. ✅ VPS 생성 완료
2. ✅ 서버 설정 완료
3. ✅ 서버 실행 완료
4. ⚠️ 종목 리스트 구현 필요
5. ⚠️ 도메인 연결 (선택사항)

**이제 컴퓨터가 꺼져 있어도 서버가 작동합니다!** 🎉

