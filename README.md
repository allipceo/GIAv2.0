# ZOBIS (Javis-Oriented Business Intelligence System)

## 🎯 프로젝트 개요

ZOBIS는 조대표님 전용 '아이언맨 자비스'급 지능형 정보 비서 시스템입니다. AI의 기술력과 비즈니스 통찰력이 결합된 최고의 비즈니스 파트너를 목표로 합니다.

## 🚀 주요 기능

### Stage 3 (현재 완료)
- ✅ **웹 검색 자동화**: Google CSE API를 통한 실시간 정보 수집
- ✅ **Notion 연동**: 자동 데이터베이스 등록 및 관리
- ✅ **AI 분석**: LLM을 통한 지능형 데이터 분석
- ✅ **403 블로커 해제**: 안정적인 API 연동 구축

### 향후 계획
- 🔄 **24시간 자동 모니터링**: 서버 배포를 통한 실시간 모니터링
- 🔄 **고급 AI 분석**: 예측 분석 및 인사이트 생성
- 🔄 **팀 협업**: 팀원들과의 실시간 정보 공유

## 📁 프로젝트 구조

```
ZOBIS/
├── src/                    # 핵심 소스코드
│   ├── utils/              # 유틸리티 (API 어댑터, Notion 연동)
│   ├── automation/         # 자동화 모듈
│   ├── classification/     # 분류 모듈
│   ├── llm_analysis/       # LLM 분석 모듈
│   ├── monitoring/         # 모니터링 모듈
│   ├── performance/        # 성능 모듈
│   └── quality/            # 품질 관리 모듈
├── scripts/                # 실행 스크립트
│   ├── a2g2n_collect_only.py      # 수집 스크립트
│   ├── a2g2n_register_from_temp.py # 등록 스크립트
│   ├── smoke_cse_test.py          # 스모크 테스트
│   └── notion_probe_and_register.py # Notion 프로브
├── docs/                   # 문서
├── config/                 # 설정 파일
├── requirements.txt        # Python 의존성
└── README.md              # 프로젝트 설명
```

## 🛠️ 설치 및 실행

### 1. 환경 설정
```bash
# 1. 저장소 클론
git clone <repository-url>
cd ZOBIS

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
# config.env 파일 생성
cp config.env.template config.env

# 실제 API 키 입력
# config.env 파일을 편집하여 실제 값 입력
```

### 3. 실행
```bash
# 스모크 테스트
python scripts/smoke_cse_test.py

# 데이터 수집
python scripts/a2g2n_collect_only.py

# Notion 등록
python scripts/a2g2n_register_from_temp.py
```

## 🔐 보안

- **환경변수 사용**: API 키는 환경변수로 관리
- **민감한 정보 보호**: .gitignore로 보호
- **정기적 보안 검토**: 보안 가이드 참조

## 📚 문서

- [보안 가이드](docs/Z071_보안가이드_및_환경변수_관리.md)
- [Stage 3 개발 경과](docs/Z064_A2G2N_Stage3_개발경과_결과_문제해결_재발방지.md)
- [사용자 시나리오](docs/Z065_ZOBIS_Stage3_사용자시나리오_및_대시보드활용가이드.md)

## 🤝 팀 협업

- **서대리**: 기술 개발 및 시스템 구축
- **나실장**: 프로젝트 총괄 및 전략 수립
- **선과장**: Notion 디자인 및 콘텐츠 관리

## 📞 지원

문제가 발생하거나 질문이 있으시면 팀원들에게 연락해 주세요.

---

**ZOBIS 팀** | 2025년 1월 17일
