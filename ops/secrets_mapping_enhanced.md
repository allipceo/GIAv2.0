# ZOBIS 시크릿 매핑 및 동기화 가이드

## 개요
ZOBIS 시스템의 민감한 정보(API 키, 토큰 등)를 안전하게 관리하기 위한 시크릿 매핑 및 동기화 절차를 정의합니다.

## 시크릿 분류

### 1. 개발 환경 (Development)
- **위치**: `.env` 파일
- **용도**: 로컬 개발 및 테스트
- **보안 수준**: 낮음 (로컬 파일)

### 2. CI/CD 환경 (GitHub Actions)
- **위치**: GitHub Secrets
- **용도**: 자동화된 빌드 및 배포
- **보안 수준**: 중간 (GitHub 암호화)

### 3. 운영 환경 (Production)
- **위치**: GCP Secret Manager
- **용도**: 실제 서비스 운영
- **보안 수준**: 높음 (Google Cloud 암호화)

## 시크릿 목록

### 핵심 시크릿
| 시크릿명 | 개발환경 | CI/CD | 운영환경 | 설명 |
|----------|----------|-------|----------|------|
| `NOTION_TOKEN` | `.env` | `NOTION_TOKEN` | `notion-token-{env}` | Notion API 토큰 |
| `HMAC_SECRET` | `.env` | `HMAC_SECRET` | `hmac-secret-{env}` | 웹훅 서명 검증용 |
| `SLACK_WEBHOOK` | `.env` | `SLACK_WEBHOOK` | `slack-webhook-{env}` | 알림 전송용 |
| `DEV_DB_ID` | `.env` | `DEV_DB_ID` | `dev-db-id-{env}` | 개발 DB ID |
| `INSURANCE_MARKET_DB_ID` | `.env` | `INSURANCE_MARKET_DB_ID` | `insurance-market-db-id-{env}` | 보험시장 DB ID |
| `Z072_PAGE_ID` | `.env` | `Z072_PAGE_ID` | `z072-page-id-{env}` | Z072 페이지 ID |

### 환경별 시크릿
| 환경 | 접두사 | 예시 |
|------|--------|------|
| `staging` | `*-staging` | `notion-token-staging` |
| `production` | `*-production` | `notion-token-production` |

## 동기화 절차

### 1. 개발 → CI/CD
```bash
# .env 파일에서 GitHub Secrets로 수동 복사
# GitHub Repository Settings > Secrets and variables > Actions
```

### 2. CI/CD → 운영
```bash
# GitHub Actions에서 GCP Secret Manager로 자동 동기화
# CD 워크플로우에서 --set-secrets 옵션 사용
```

### 3. 운영 → 개발 (역동기화)
```bash
# GCP Secret Manager에서 로컬 .env로 수동 복사
# 보안상 자동화하지 않음
```

## 보안 정책

### 1. 접근 권한
- **개발자**: 개발 환경 시크릿 접근 가능
- **CI/CD**: GitHub Actions를 통한 제한적 접근
- **운영**: GCP IAM을 통한 역할 기반 접근

### 2. 암호화
- **개발**: 평문 저장 (로컬 파일)
- **CI/CD**: GitHub 암호화
- **운영**: GCP KMS 암호화

### 3. 로테이션
- **주기**: 분기별 (3개월)
- **방법**: 새 시크릿 생성 → 배포 → 이전 시크릿 삭제
- **자동화**: GitHub Actions 워크플로우

## 모니터링 및 감사

### 1. 접근 로그
- **GitHub Actions**: Actions 탭에서 실행 로그 확인
- **GCP**: Cloud Audit Logs에서 시크릿 접근 로그 확인

### 2. 알림 설정
- **시크릿 변경**: Slack 알림
- **비정상 접근**: 이메일 + Slack 알림
- **만료 예정**: 30일 전 알림

## 문제 해결

### 1. 시크릿 누락
```bash
# GitHub Actions에서 시크릿 확인
echo "Checking secrets..."
if [ -z "$NOTION_TOKEN" ]; then
    echo "❌ NOTION_TOKEN not found"
    exit 1
fi
```

### 2. 권한 오류
```bash
# GCP 서비스 계정 권한 확인
gcloud projects get-iam-policy $PROJECT_ID
```

### 3. 동기화 실패
```bash
# 시크릿 값 검증
gcloud secrets versions access latest --secret="notion-token-staging"
```

## 체크리스트

### 배포 전 확인사항
- [ ] 모든 시크릿이 올바른 환경에 설정됨
- [ ] GitHub Actions에서 시크릿 접근 가능
- [ ] GCP Secret Manager에서 시크릿 존재
- [ ] 권한 설정이 올바름
- [ ] 로그 모니터링 활성화

### 배포 후 확인사항
- [ ] 애플리케이션이 시크릿에 정상 접근
- [ ] 외부 API 호출 성공
- [ ] 알림 시스템 정상 작동
- [ ] 보안 로그 정상 생성

## 참고 자료
- [GitHub Secrets 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GCP Secret Manager 문서](https://cloud.google.com/secret-manager/docs)
- [ZOBIS 보안 정책](docs/security-policy.md)
