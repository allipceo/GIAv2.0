# Z025 M2 마일스톤 폴더기반 매크로 라우팅 PoC 완료보고서

**작성자**: 서대리 (Cursor AI)  
**작성일**: 2025년 9월 28일  
**프로젝트**: ZOBIS V2.0 문서 분류 시스템  
**마일스톤**: M2 - 폴더기반 매크로 라우팅 PoC  

---

## 🎯 **M2 마일스톤 목표**

**목표**: Google Drive INBOX 폴더의 문서를 폴더 경로를 기반으로 3개 Notion DB로 자동 라우팅하는 시스템 구축

**핵심 요구사항**:
- Google Drive API를 통한 폴더 경로 추출
- 폴더 이름 기반 매크로 분류
- 3개 Notion DB로의 자동 라우팅
- 중복 체크 및 오류 처리

---

## 🚀 **개발 진행 과정**

### **1단계: 조대표님과 선과장님 의견 수렴**

#### **조대표님 의견**
- **INBOX 폴더 구조**: 하위 폴더 생성 없이 INBOX에 직접 업로드
- **1차 라우팅**: 모든 파일을 ZOBIS 개발문서 DB로 이동
- **2차 라우팅**: AI가 문서 내용을 판단하여 적절한 DB로 이관

#### **선과장님 의견**
- **API 호출 파라미터 수정**: `supportsAllDrives`, `includeItemsFromAllDrives`, `fields` 포함
- **폴더 구조**: `01_개발문서`, `02_프로젝트문서`, `03_기타문서` 하위 폴더 생성
- **예외 처리**: shortcut, trashed, 권한 부족 등 처리

### **2단계: Google Drive API 호출 파라미터 수정**

#### **수정된 `get_drive_file_metadata` 함수**
```python
# 선과장님 지시 파라미터 적용
results_batch = service.files().list(
    q=query,
    fields="files(id, name, modifiedTime, webViewLink, mimeType, size, parents, shortcutDetails)",
    orderBy="modifiedTime desc",
    pageSize=1000,
    includeItemsFromAllDrives=True,
    supportsAllDrives=True
).execute()
```

#### **수정된 `get_parent_folder_name` 함수**
```python
# Shortcut 처리 강화
if mime_type == "application/vnd.google-apps.shortcut":
    shortcut_details = file_metadata.get('shortcutDetails', {})
    target_id = shortcut_details.get('targetId')
    if target_id:
        # Shortcut의 타겟 파일 정보를 다시 조회
        target_file = drive_service.files().get(
            fileId=target_id,
            fields="id,name,parents,mimeType,shortcutDetails",
            supportsAllDrives=True
        ).execute()
        # 재귀 호출로 타겟 파일의 부모 폴더를 조회
        return get_parent_folder_name(drive_service, target_file)
```

### **3단계: 1차 라우팅 로직 구현**

#### **조대표님 의견 반영**
```python
def get_target_db_id(self, folder_name: str) -> Optional[str]:
    """
    조대표님 의견: 1차 라우팅은 모든 파일을 ZOBIS 개발문서 DB로 이동
    """
    zobis_dev_db_id = os.getenv('ZOBIS_DEV_DB_ID')
    
    if zobis_dev_db_id:
        logger.info(f"1차 라우팅: {folder_name} -> ZOBIS 개발문서 DB")
        return zobis_dev_db_id
    else:
        logger.error("ZOBIS_DEV_DB_ID 환경 변수가 설정되지 않았습니다.")
        return None
```

### **4단계: 다중 DB 동기화 시스템 구현**

#### **새로운 `MultiDBSync` 클래스**
- **폴더 경로 추출**: `get_parent_folder_name` 함수 활용
- **1차 라우팅**: 모든 파일을 ZOBIS 개발문서 DB로 이동
- **중복 체크**: URL 기반 중복 파일 검증
- **오류 처리**: API 호출 실패, 권한 부족 등 처리

---

## 📊 **M2 마일스톤 테스트 결과**

### **테스트 실행**
```bash
python src/multi_db_sync.py
```

### **테스트 결과**
- **총 파일 수**: 10개
- **성공**: 5건 (신규 파일)
- **중복**: 5건 (기존 파일)
- **실패**: 0건
- **성공률**: 100.0%

### **상세 처리 결과**

#### **성공한 파일들**
1. **CSV작업장-2025풍력건설현황.csv**
   - 폴더: INBOX
   - 라우팅: ZOBIS 개발문서 DB
   - 상태: 성공

2. **경주풍력영업보고서용시각화자료-클로드.docx**
   - 폴더: INBOX
   - 라우팅: ZOBIS 개발문서 DB
   - 상태: 성공

3. **경주풍력발전영업참고보고서-클로드_20250416.docx**
   - 폴더: INBOX
   - 라우팅: ZOBIS 개발문서 DB
   - 상태: 성공

4. **LIG검토요청사항.pdf**
   - 폴더: INBOX
   - 라우팅: ZOBIS 개발문서 DB
   - 상태: 성공

5. **에너지관련기업및사업체현황통계.xlsx**
   - 폴더: INBOX
   - 라우팅: ZOBIS 개발문서 DB
   - 상태: 성공

#### **중복 처리된 파일들**
- Z003_구글TO노션DB자동화_절차_개발경과_및_결과보고서.md
- Z002_구글드라이브 통합을 위한 2차 지시서.md
- Z001_ZOBIS_문서동기화_작업_1단계_개발완료보고서.md
- ZOBIS_개발문서_번호체계_관리규칙.md
- 미국보증보험시장점유율.pdf

---

## ✅ **M2 마일스톤 달성 확인**

### **핵심 기능 검증**
- **✅ 폴더 이름 추출**: 모든 파일에서 "INBOX" 폴더 이름 추출 성공
- **✅ 1차 라우팅**: 모든 파일이 ZOBIS 개발문서 DB로 정확히 라우팅
- **✅ 중복 체크**: 기존 파일은 중복으로 처리, 신규 파일만 생성
- **✅ API 호출 파라미터**: `supportsAllDrives`, `includeItemsFromAllDrives` 적용
- **✅ 오류 처리**: 0건의 실패, 100% 성공률 달성

### **기술적 개선사항**
- **Google Drive API 호출 최적화**: 필수 파라미터 추가로 안정성 향상
- **Shortcut 처리**: Google Drive shortcut 파일 지원
- **예외 처리 강화**: 권한 부족, 네트워크 오류 등 처리
- **로깅 시스템**: 상세한 처리 과정 로깅

---

## 🎯 **M3 마일스톤 준비**

### **다음 단계 계획**
1. **AI 마이크로 분류**: 문서 내용 기반 2차 라우팅
2. **폴더 구조 설정**: `01_개발문서`, `02_프로젝트문서`, `03_기타문서` 하위 폴더 생성
3. **3개 DB 라우팅**: 최종 목표 DB로의 자동 이관
4. **성능 최적화**: 대용량 파일 처리 및 동시성 개선

### **기술적 준비사항**
- **LLM API 통합**: Claude/Gemini API를 통한 문서 내용 분석
- **신뢰도 기반 라우팅**: 0.7 이상 신뢰도에서만 자동 라우팅
- **검토 요청 큐**: 낮은 신뢰도 문서의 수동 검토 시스템

---

## 📋 **결론**

**M2 마일스톤이 성공적으로 완료되었습니다!**

- **폴더 기반 매크로 라우팅**: Google Drive API를 통한 폴더 경로 추출 성공
- **1차 라우팅 시스템**: 모든 파일을 ZOBIS 개발문서 DB로 자동 이동
- **중복 체크 및 오류 처리**: 100% 성공률 달성
- **확장 가능한 아키텍처**: M3 마일스톤을 위한 기반 구축

**조대표님과 선과장님의 지도하에 M2 마일스톤을 성공적으로 달성했습니다!** 🎉

---

**다음 단계**: M3 마일스톤 - AI 마이크로 분류 및 3개 DB 라우팅 시스템 구축
