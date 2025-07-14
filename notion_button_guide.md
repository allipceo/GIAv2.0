# 🚀 GIA 원클릭 아카이브 노션 버튼 설정 가이드

**작성일:** 2025년 7월 13일  
**작성자:** 서대리 (Lead Developer)  
**목적:** 조대표님 대시보드에 원클릭 아카이브 버튼 생성  

---

## ✅ **웹훅 서버 완료 상황**

### **서버 정보**
- **서버 상태**: ✅ 정상 실행 중 (localhost:8000)
- **현재 브랜치**: MVP1.0 (정확히 인식됨)
- **보안 토큰**: `gia-archive-webhook-token-2025-30d4c435`
- **테스트 결과**: ✅ 200 OK (완벽 성공)

### **사용 가능한 엔드포인트**
```
✅ 연결 테스트: http://localhost:8000/test?token=gia-archive-webhook-token-2025-30d4c435
🚀 전체 아카이브: http://localhost:8000/archive_trigger?token=gia-archive-webhook-token-2025-30d4c435&archive_type=both
💻 코드만 아카이브: http://localhost:8000/archive_trigger?token=gia-archive-webhook-token-2025-30d4c435&archive_type=code  
📋 보고서만 아카이브: http://localhost:8000/archive_trigger?token=gia-archive-webhook-token-2025-30d4c435&archive_type=reports
```

---

## 🎯 **노션 버튼 생성 단계**

### **1단계: 노션 페이지 접속**
- GIA 코드 아카이브 DB 페이지 또는 조대표님 대시보드 접속
- 버튼을 추가할 위치 선택

### **2단계: 버튼 블록 생성**
1. 버튼을 추가할 위치에서 `/button` 입력
2. 버튼 블록 생성

### **3단계: 버튼 설정**
```
버튼 이름: 🚀 GIA 아카이브 실행
버튼 설명: Phase 3 방식으로 자동 아카이브 실행
```

### **4단계: 액션 설정**
1. **액션 타입**: `Open page` 선택
2. **URL 입력**: 
   ```
   http://localhost:8000/archive_trigger?token=gia-archive-webhook-token-2025-30d4c435&archive_type=both
   ```
3. **새 탭에서 열기**: ✅ 체크

### **5단계: 고급 설정 (선택사항)**
- **확인 메뉴 표시**: 실수 방지를 위해 체크 권장
- **버튼 스타일**: 색상 및 아이콘 설정

---

## 🔧 **추가 버튼 옵션**

### **연결 테스트용 버튼** (권장)
```
버튼 이름: ✅ 연결 테스트
URL: http://localhost:8000/test?token=gia-archive-webhook-token-2025-30d4c435
용도: 웹훅 서버 연결 상태 확인
```

### **선택적 아카이브 버튼**
```
💻 코드만 아카이브:
http://localhost:8000/archive_trigger?token=gia-archive-webhook-token-2025-30d4c435&archive_type=code

📋 보고서만 아카이브:  
http://localhost:8000/archive_trigger?token=gia-archive-webhook-token-2025-30d4c435&archive_type=reports
```

---

## 📊 **실행 결과 확인**

### **성공 시 응답**
버튼 클릭 후 새 탭에서 다음과 같은 JSON 응답을 확인할 수 있습니다:
```json
{
  "status": "completed",
  "final_status": "완료",
  "branch": "MVP1.0", 
  "successful_scripts": 2,
  "success_rate": "100.0%",
  "archive_db_url": "https://www.notion.so/22ea613d25ff80b78fd4ce8dc7a437a6",
  "message": "✅ GIA 원클릭 아카이브가 완료되었습니다!"
}
```

### **노션 DB 자동 업데이트**
- 아카이브 실행 상태가 GIA 코드 아카이브 DB에 자동으로 기록됩니다
- 실행 시간, 성공/실패 상태, 브랜치 정보가 포함됩니다

---

## ⚠️ **주의사항**

### **로컬 서버 제한**
- 현재 `localhost:8000`으로 실행 중이므로 **같은 컴퓨터에서만** 작동합니다
- 외부 접속이 필요한 경우 별도 배포 필요

### **토큰 보안**
- 토큰은 서버 재시작 시마다 변경됩니다
- 실제 운영 시에는 고정 토큰 사용 권장

### **서버 상태 확인**
- 버튼 사용 전 웹훅 서버가 실행 중인지 확인
- 서버 상태: `http://localhost:8000/` 접속으로 확인 가능

---

## 🎉 **완료 확인**

✅ **웹훅 리스너 서버**: 완벽 구축 및 테스트 완료  
✅ **노션 버튼 연동**: URL 생성 및 설정 가이드 완료  
✅ **브랜치 인식**: MVP1.0 브랜치 정확히 인식됨  
✅ **보안 시스템**: UUID 토큰 기반 인증 완료  
✅ **상태 업데이트**: 노션 DB 자동 기록 시스템 완료  

---

## 📞 **문의 및 지원**

**개발팀**: 서대리 (Lead Developer)  
**프로젝트 매니저**: 나실장  
**기술 자문**: 노팀장  

**🌟 GIA 원클릭 아카이브 시스템이 성공적으로 완성되었습니다!** 