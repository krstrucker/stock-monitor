# VPS/SSH 서버 배포 가이드

## SSH 서버란?

**VPS (Virtual Private Server)**를 사용하면:
- ✅ 24시간 항상 켜져 있는 서버
- ✅ SSH로 원격 접속하여 관리
- ✅ 컴퓨터가 꺼져 있어도 작동
- ✅ 완전한 제어권

## VPS 서비스 추천

### 1. DigitalOcean (추천) ⭐
- **가격**: 월 $4~6 (가장 저렴)
- **장점**: 간단한 설정, 빠른 속도
- **URL**: https://www.digitalocean.com

### 2. AWS EC2
- **가격**: 월 $3.5~ (무료 티어 있음)
- **장점**: 안정적, 다양한 옵션
- **URL**: https://aws.amazon.com/ec2

### 3. Google Cloud Platform
- **가격**: 월 $3.5~ (무료 크레딧 제공)
- **장점**: Google 인프라
- **URL**: https://cloud.google.com

### 4. Linode
- **가격**: 월 $5~
- **장점**: 간단한 인터페이스
- **URL**: https://www.linode.com

### 5. Vultr
- **가격**: 월 $2.5~ (가장 저렴)
- **장점**: 매우 저렴, 빠른 속도
- **URL**: https://www.vultr.com

## DigitalOcean 배포 방법 (예시)

### 1단계: VPS 생성

1. **DigitalOcean 가입**
   - https://www.digitalocean.com 접속
   - 계정 생성

2. **Droplet 생성**
   - "Create" → "Droplets" 클릭
   - OS: Ubuntu 22.04 선택
   - Plan: Basic $4/mo 선택 (충분함)
   - Region: 가장 가까운 지역 선택
   - Authentication: SSH keys 또는 Password
   - "Create Droplet" 클릭

3. **IP 주소 확인**
   - 생성된 Droplet의 IP 주소 복사
   - 예: `123.45.67.89`

### 2단계: SSH 접속

**Windows에서:**
```powershell
# PowerShell에서 SSH 접속
ssh root@123.45.67.89
# 또는
ssh root@your-droplet-ip
```

**비밀번호 입력 후 접속 완료!**

### 3단계: 서버 설정

```bash
# 시스템 업데이트
apt update && apt upgrade -y

# Python 설치
apt install python3 python3-pip git -y

# 프로젝트 클론
cd /root
git clone https://github.com/your-username/stock-monitor.git
cd stock-monitor

# 패키지 설치
pip3 install -r requirements.txt
```

### 4단계: 환경 변수 설정

```bash
# .env 파일 생성
nano .env
```

다음 내용 추가:
```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
MONITOR_SYMBOL_COUNT=0
MONITOR_WORKERS=20
MONITOR_TIMEFRAME=short_swing
PORT=5000
HOST=0.0.0.0
```

저장: `Ctrl+X`, `Y`, `Enter`

### 5단계: 서버 실행 (백그라운드)

**방법 1: screen 사용 (간단)**
```bash
# screen 설치
apt install screen -y

# screen 세션 시작
screen -S stock-server

# 서버 실행
python3 server.py

# 세션 분리: Ctrl+A, D
# 세션 다시 접속: screen -r stock-server
```

**방법 2: systemd 서비스 (권장)**
```bash
# 서비스 파일 생성
nano /etc/systemd/system/stock-monitor.service
```

다음 내용 추가:
```ini
[Unit]
Description=Stock Monitor Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/stock-monitor
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /root/stock-monitor/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 활성화:
```bash
systemctl daemon-reload
systemctl enable stock-monitor
systemctl start stock-monitor
systemctl status stock-monitor
```

### 6단계: 방화벽 설정

```bash
# UFW 방화벽 설정
ufw allow 22/tcp    # SSH
ufw allow 5000/tcp  # Flask 서버
ufw enable
```

### 7단계: 완료!

- 서버가 백그라운드에서 실행 중
- `http://your-ip:5000` 접속 가능
- 24시간 항상 켜져 있음

## VPS vs 클라우드 서비스 비교

| 항목 | VPS (SSH) | Railway/Render |
|------|-----------|----------------|
| 가격 | 월 $2.5~6 | 무료~유료 |
| 제어권 | ✅ 완전한 제어 | ⚠️ 제한적 |
| 설정 난이도 | ⭐⭐⭐ 어려움 | ⭐ 쉬움 |
| 유지보수 | 직접 관리 | 자동 관리 |
| 추천 대상 | 서버 관리 경험 있음 | 초보자 |

## 장점

✅ **완전한 제어권**
- 원하는 대로 설정 가능
- 모든 권한

✅ **저렴한 비용**
- 월 $2.5~6 정도
- 충분한 성능

✅ **24시간 작동**
- 컴퓨터가 꺼져 있어도 작동
- 안정적

## 단점

⚠️ **설정이 복잡함**
- SSH 접속 필요
- 서버 관리 지식 필요

⚠️ **직접 관리 필요**
- 업데이트 직접 해야 함
- 문제 발생 시 직접 해결

## 추천

**초보자**: Railway/Render (간단함)
**경험자**: VPS/SSH 서버 (완전한 제어)

## 다음 단계

1. VPS 서비스 선택 (DigitalOcean 추천)
2. Droplet 생성
3. SSH 접속
4. 서버 설정 및 실행
5. 완료!

**이제 컴퓨터가 꺼져 있어도 서버가 작동합니다!** 🎉

