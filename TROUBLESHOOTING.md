# 문제 해결 가이드

## SSL 인증서 오류 해결 방법

### 증상
```
curl: (77) error setting certificate verify locations
Failed to get ticker 'AAPL' reason: ...
```

### 해결 방법

#### 방법 1: PowerShell에서 인코딩 설정 후 실행 (권장)
```powershell
# PowerShell에서 실행
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
python main.py
```

#### 방법 2: certifi 재설치
```bash
pip uninstall certifi -y
pip install certifi
```

#### 방법 3: 모든 관련 패키지 업그레이드
```bash
pip install --upgrade certifi requests urllib3 yfinance curl-cffi
```

#### 방법 4: 환경 변수 설정 (Windows)
PowerShell에서:
```powershell
$env:CURL_CA_BUNDLE = ""
$env:REQUESTS_CA_BUNDLE = ""
python main.py
```

또는 명령 프롬프트에서:
```cmd
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
python main.py
```

#### 방법 5: Python 재설치
만약 위 방법들이 모두 실패한다면, Python을 최신 버전으로 재설치하는 것을 고려해보세요.

### 추가 확인사항

1. **인터넷 연결**: 안정적인 인터넷 연결이 필요합니다.
2. **방화벽/프록시**: 회사 네트워크나 방화벽이 SSL 연결을 차단할 수 있습니다.
3. **VPN**: VPN을 사용 중이라면 일시적으로 끄고 시도해보세요.
4. **안티바이러스**: 일부 안티바이러스가 SSL 연결을 차단할 수 있습니다.

### 임시 해결책

현재 코드는 SSL 검증을 우회하도록 설정되어 있지만, yfinance가 내부적으로 curl을 사용하는 경우 여전히 문제가 발생할 수 있습니다.

가장 확실한 방법은 **방법 1 (PowerShell 인코딩 설정)**을 사용하는 것입니다.

