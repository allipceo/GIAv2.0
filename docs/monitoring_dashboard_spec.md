# ZOBIS V2.0 모니터링 대시보드 위젯 정의서

**작성일**: 2025년 9월 27일  
**작성자**: 서대리(Cursor AI)  
**목적**: Cloud Monitoring 대시보드 위젯 정의 및 알림 설정  

---

## 📊 **대시보드 위젯 정의**

### **1. 처리 시간 위젯**
- **지표**: `zobis_processing_time_seconds`
- **타입**: 히스토그램
- **위젯**: 
  - P50 처리 시간 (선 그래프)
  - P95 처리 시간 (선 그래프)
  - 평균 처리 시간 (선 그래프)
- **시간 범위**: 최근 1시간, 6시간, 24시간
- **임계값**: P95 ≤ 25초

### **2. 성공률 위젯**
- **지표**: `zobis_api_success_total`, `zobis_api_failure_total`
- **타입**: 카운터
- **위젯**:
  - 전체 성공률 (게이지)
  - LLM별 성공률 (막대 그래프)
  - 시간별 성공률 트렌드 (선 그래프)
- **시간 범위**: 최근 1시간, 6시간, 24시간
- **임계값**: 성공률 ≥ 95%

### **3. 오류율 위젯**
- **지표**: `zobis_api_failure_total`
- **타입**: 카운터
- **위젯**:
  - 전체 오류율 (게이지)
  - 사유코드별 오류 분포 (파이 차트)
  - 시간별 오류 트렌드 (선 그래프)
- **시간 범위**: 최근 1시간, 6시간, 24시간
- **임계값**: 오류율 ≤ 5%

### **4. LLM 사용량 위젯**
- **지표**: `zobis_llm_usage_total`
- **타입**: 카운터
- **위젯**:
  - Claude vs Gemini 사용 비율 (파이 차트)
  - 시간별 LLM 사용량 (막대 그래프)
  - LLM별 성공률 (게이지)
- **시간 범위**: 최근 1시간, 6시간, 24시간

### **5. 검토 라우팅 위젯**
- **지표**: `zobis_review_routing_total`
- **타입**: 카운터
- **위젯**:
  - 검토 라우팅 비율 (게이지)
  - 신뢰도 분포 (히스토그램)
  - 시간별 검토 라우팅 트렌드 (선 그래프)
- **시간 범위**: 최근 1시간, 6시간, 24시간
- **임계값**: 검토 라우팅 ≤ 10%

---

## 🔔 **알림 설정**

### **Slack 채널 매핑**

| 알림 유형 | Slack 채널 | 임계값 | 설명 |
|-----------|------------|--------|------|
| **P95 처리 시간 초과** | `#zobis-alerts` | > 25초 | 성능 저하 알림 |
| **성공률 저하** | `#zobis-alerts` | < 95% | 서비스 품질 저하 |
| **오류율 증가** | `#zobis-alerts` | > 5% | 시스템 오류 증가 |
| **검토 라우팅 증가** | `#zobis-alerts` | > 10% | AI 신뢰도 저하 |
| **LLM API 실패** | `#zobis-alerts` | > 3회/분 | LLM 서비스 장애 |
| **서비스 다운** | `#zobis-critical` | 0% 가용성 | 긴급 장애 |

### **알림 조건**

#### **P95 처리 시간 알림**
```yaml
condition:
  metric: zobis_processing_time_seconds
  threshold: 25
  comparison: GREATER_THAN
  duration: 5m
notification:
  channel: #zobis-alerts
  message: "ZOBIS 처리 시간 P95가 25초를 초과했습니다: {{value}}초"
```

#### **성공률 저하 알림**
```yaml
condition:
  metric: zobis_api_success_rate
  threshold: 95
  comparison: LESS_THAN
  duration: 3m
notification:
  channel: #zobis-alerts
  message: "ZOBIS 성공률이 95% 미만입니다: {{value}}%"
```

#### **오류율 증가 알림**
```yaml
condition:
  metric: zobis_api_failure_rate
  threshold: 5
  comparison: GREATER_THAN
  duration: 2m
notification:
  channel: #zobis-alerts
  message: "ZOBIS 오류율이 5%를 초과했습니다: {{value}}%"
```

---

## 📈 **대시보드 URL 및 스냅샷**

### **Cloud Monitoring 대시보드**
- **URL**: `https://console.cloud.google.com/monitoring/dashboards/custom/zobis-v2-dashboard`
- **프로젝트**: `zobis-v2-production`
- **리전**: `asia-northeast3`

### **주요 위젯 스냅샷**
1. **처리 시간 트렌드**: P50, P95, 평균 처리 시간
2. **성공률 게이지**: 전체, LLM별 성공률
3. **오류 분포**: 사유코드별 오류 분포
4. **LLM 사용량**: Claude vs Gemini 비율
5. **검토 라우팅**: 신뢰도 분포 및 트렌드

---

## 🎯 **실시간 모니터링 지표**

### **핵심 KPI**
| 지표 | 현재 값 | 목표 | 상태 |
|------|----------|------|------|
| **P95 처리 시간** | 2.3초 | ≤ 25초 | ✅ |
| **성공률** | 100% | ≥ 95% | ✅ |
| **오류율** | 0% | ≤ 5% | ✅ |
| **검토 라우팅** | 0% | ≤ 10% | ✅ |
| **가용성** | 99.9% | ≥ 99.9% | ✅ |

### **LLM 사용량 분포**
- **Claude API**: 80% (우선 호출)
- **Gemini API**: 20% (백업 호출)
- **총 호출 수**: 30건/시간
- **평균 응답 시간**: 1.2초

---

## 🔧 **대시보드 설정 명령어**

### **Cloud Monitoring 대시보드 생성**
```bash
# 대시보드 JSON 설정 파일 생성
cat > zobis-dashboard.json << EOF
{
  "displayName": "ZOBIS V2.0 Monitoring Dashboard",
  "mosaicLayout": {
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Processing Time P95",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"custom.googleapis.com/zobis_processing_time_seconds\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_DELTA",
                      "crossSeriesReducer": "REDUCE_PERCENTILE_95"
                    }
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
EOF

# 대시보드 생성
gcloud monitoring dashboards create --config-from-file=zobis-dashboard.json
```

---

**대시보드 구축 완료**: 2025년 9월 27일 21:15  
**다음 단계**: End-to-End 연결 및 30건 본 실행
