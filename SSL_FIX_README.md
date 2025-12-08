# SSL 인증서 문제 해결 가이드

## 문제 상황
`curl: (77) error setting certificate verify locations` 오류가 발생하는 경우

## 해결 방법

### 방법 1: certifi 재설치 (권장)
```bash
pip uninstall certifi -y
pip install certifi
```

### 방법 2: yfinance 최신 버전으로 업그레이드
```bash
pip install --upgrade yfinance
```

### 방법 3: 모든 관련 패키지 업그레이드
```bash
pip install --upgrade certifi requests urllib3 yfinance
```

### 방법 4: Python 재설치 (최후의 수단)
만약 위 방법들이 모두 실패한다면, Python을 재설치하는 것을 고려해보세요.

## 추가 확인사항

1. **인터넷 연결 확인**: 안정적인 인터넷 연결이 필요합니다.
2. **방화벽/프록시**: 회사 네트워크나 방화벽이 SSL 연결을 차단할 수 있습니다.
3. **VPN**: VPN을 사용 중이라면 일시적으로 끄고 시도해보세요.

## 임시 해결책

만약 위 방법들이 모두 실패한다면, 시스템이 SSL 검증을 우회하도록 설정되어 있습니다.
하지만 보안상 권장되지 않으므로, 가능하면 위의 방법들을 먼저 시도해보세요.

