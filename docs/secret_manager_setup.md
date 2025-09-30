# ZOBIS V2.0 Secret Manager 설정 가이드

**작성일**: 2025년 9월 27일  
**작성자**: 서대리(Cursor AI)  
**목적**: 환경 변수에서 Google Secret Manager로 시크릿 이관  

---

## 🔐 **Secret Manager 전환 계획**

### **현재 환경 변수 → Secret Manager 매핑**

| 환경 변수 | Secret Manager 키 | 설명 | 롤링 주기 |
|-----------|------------------|------|-----------|
| `NOTION_TOKEN` | `zobis-notion-token` | Notion API 토큰 | 90일 |
| `CLAUDE_API_KEY` | `zobis-claude-api-key` | Claude API 키 | 90일 |
| `GEMINI_API_KEY` | `zobis-gemini-api-key` | Gemini API 키 | 90일 |
| `SERVER_SIDE_TOKEN` | `zobis-server-token` | 웹훅 서버 토큰 | 30일 |
| `HMAC_SECRET` | `zobis-hmac-secret` | HMAC 서명 시크릿 | 30일 |
| `GOOGLE_DRIVE_FOLDER_ID` | `zobis-drive-folder-id` | Google Drive 폴더 ID | 1년 |
| `NOTION_DATABASE_ID` | `zobis-notion-db-id` | Notion 데이터베이스 ID | 1년 |

---

## 🛠️ **Secret Manager 설정 명령어**

### **1. Secret 생성**
```bash
# Notion API 토큰
gcloud secrets create zobis-notion-token \
    --data-file=- \
    --replication-policy="automatic"

# Claude API 키
gcloud secrets create zobis-claude-api-key \
    --data-file=- \
    --replication-policy="automatic"

# Gemini API 키
gcloud secrets create zobis-gemini-api-key \
    --data-file=- \
    --replication-policy="automatic"

# 서버 토큰
gcloud secrets create zobis-server-token \
    --data-file=- \
    --replication-policy="automatic"

# HMAC 시크릿
gcloud secrets create zobis-hmac-secret \
    --data-file=- \
    --replication-policy="automatic"

# Google Drive 폴더 ID
gcloud secrets create zobis-drive-folder-id \
    --data-file=- \
    --replication-policy="automatic"

# Notion 데이터베이스 ID
gcloud secrets create zobis-notion-db-id \
    --data-file=- \
    --replication-policy="automatic"
```

### **2. Cloud Run 서비스 계정 권한 설정**
```bash
# Secret Manager Secret Accessor 역할 부여
gcloud projects add-iam-policy-binding zobis-v2-production \
    --member="serviceAccount:zobis-webhook-server@zobis-v2-production.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### **3. Cloud Run 환경 변수 설정**
```bash
gcloud run services update zobis-webhook-server \
    --region=asia-northeast3 \
    --set-secrets="NOTION_TOKEN=zobis-notion-token:latest,CLAUDE_API_KEY=zobis-claude-api-key:latest,GEMINI_API_KEY=zobis-gemini-api-key:latest,SERVER_SIDE_TOKEN=zobis-server-token:latest,HMAC_SECRET=zobis-hmac-secret:latest,GOOGLE_DRIVE_FOLDER_ID=zobis-drive-folder-id:latest,NOTION_DATABASE_ID=zobis-notion-db-id:latest"
```

---

## 🔄 **롤링 절차**

### **API 키 롤링 (90일 주기)**
1. **새 키 생성**: API 제공자에서 새 키 생성
2. **Secret 업데이트**: `gcloud secrets versions add` 명령으로 새 버전 추가
3. **서비스 재시작**: Cloud Run 서비스 재배포로 새 키 적용
4. **검증**: 헬스체크 및 기능 테스트
5. **이전 키 삭제**: 검증 완료 후 이전 버전 삭제

### **서버 토큰 롤링 (30일 주기)**
1. **새 토큰 생성**: 랜덤 문자열 생성
2. **Secret 업데이트**: 새 버전 추가
3. **클라이언트 업데이트**: Notion Automation Rule 업데이트
4. **서비스 재시작**: Cloud Run 서비스 재배포
5. **검증**: 웹훅 테스트

---

## 📊 **보안 강화 효과**

### **Before (환경 변수)**
- ❌ 평문 저장
- ❌ 버전 관리 없음
- ❌ 접근 로그 없음
- ❌ 자동 롤링 없음

### **After (Secret Manager)**
- ✅ 암호화 저장
- ✅ 버전 관리
- ✅ 접근 로그 추적
- ✅ 자동 롤링 지원
- ✅ IAM 기반 접근 제어

---

## 🚨 **비상 대응 절차**

### **시크릿 노출 시**
1. **즉시 비활성화**: 해당 시크릿 버전 비활성화
2. **새 시크릿 생성**: 새 키/토큰 생성
3. **서비스 업데이트**: 새 시크릿으로 서비스 업데이트
4. **클라이언트 업데이트**: 관련 시스템 업데이트
5. **보안 감사**: 접근 로그 분석

### **서비스 장애 시**
1. **이전 버전 복구**: 안정적인 이전 버전으로 롤백
2. **문제 분석**: 로그 및 메트릭 분석
3. **수정 배포**: 문제 해결 후 재배포
4. **검증**: 전체 기능 테스트

---

**보안 강화 완료**: 2025년 9월 27일 21:00  
**다음 단계**: 모니터링 대시보드 구축
