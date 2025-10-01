# S4-006: Notion 실행버튼 시스템 구축 방안

**작성일**: 2025년 10월 1일 20:00  
**작성자**: 서대리 (Cursor AI)  
**목적**: Notion에서 실행버튼을 통한 CASE1,2,3 자동 실행 시스템 구축 방안 제안

## 🎯 **구축 목표**

### **문제점**
- 조대표님이 Notion에서 직접 서대리에게 명령어를 전달할 수 없음
- CASE1,2,3 작업을 매번 수동으로 실행해야 하는 불편함
- Notion과 로컬 환경 간의 연동 부재

### **해결 방안**
- **Notion 실행버튼**을 통한 원클릭 자동 실행
- **웹훅 연동**으로 Notion → 서대리 시스템 자동 트리거
- **실행 결과 자동 피드백**을 Notion으로 반환

## 🚀 **시스템 구조**

### **1. 전체 아키텍처**

```
Notion 페이지
├── [케이스1 실행] 버튼 → Notion Automation
├── [케이스2 실행] 버튼 → Notion Automation  
├── [케이스3 실행] 버튼 → Notion Automation
└── [전체 실행] 버튼 → Notion Automation
                    ↓
            웹훅 (Webhook)
                    ↓
        서대리 시스템 (로컬/서버)
        ├── CASE1 핸들러
        ├── CASE2 핸들러
        ├── CASE3 핸들러
        └── 결과 피드백
                    ↓
            Notion 페이지 업데이트
```

### **2. Notion Automation 설정**

#### **케이스1 실행버튼**
```json
{
  "trigger": "button_click",
  "button_name": "케이스1 실행",
  "action": "webhook",
  "webhook_url": "http://localhost:8000/webhook/case1",
  "payload": {
    "case": "case1",
    "target": "Z062",
    "notion_page_id": "{{page_id}}"
  }
}
```

#### **케이스2 실행버튼**
```json
{
  "trigger": "button_click", 
  "button_name": "케이스2 실행",
  "action": "webhook",
  "webhook_url": "http://localhost:8000/webhook/case2",
  "payload": {
    "case": "case2",
    "target": "Z062",
    "notion_page_id": "{{page_id}}"
  }
}
```

#### **케이스3 실행버튼**
```json
{
  "trigger": "button_click",
  "button_name": "케이스3 실행", 
  "action": "webhook",
  "webhook_url": "http://localhost:8000/webhook/case3",
  "payload": {
    "case": "case3",
    "target": "Z062",
    "notion_page_id": "{{page_id}}"
  }
}
```

## 🔧 **서대리 시스템 구현**

### **1. 웹훅 서버 구축**

```python
# webhook_server.py
from flask import Flask, request, jsonify
import subprocess
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook/case1', methods=['POST'])
def handle_case1():
    """케이스1 실행버튼 처리"""
    data = request.json
    target = data.get('target', 'Z062')
    
    # 케이스1 실행
    result = subprocess.run([
        'python', 'scripts/run_notion_workflow.py',
        '--case', '1',
        '--target', target,
        '--out', f'logs/webhook_case1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    ], capture_output=True, text=True)
    
    # Notion 페이지 업데이트
    update_notion_page(data['notion_page_id'], {
        'status': 'success' if result.returncode == 0 else 'failed',
        'message': '케이스1 실행 완료',
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'status': 'success'})

@app.route('/webhook/case2', methods=['POST'])
def handle_case2():
    """케이스2 실행버튼 처리"""
    data = request.json
    target = data.get('target', 'Z062')
    
    # 케이스2 실행
    result = subprocess.run([
        'python', 'scripts/run_notion_workflow.py',
        '--case', '2', 
        '--target', target,
        '--out', f'logs/webhook_case2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    ], capture_output=True, text=True)
    
    # Notion 페이지 업데이트
    update_notion_page(data['notion_page_id'], {
        'status': 'success' if result.returncode == 0 else 'failed',
        'message': '케이스2 실행 완료',
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'status': 'success'})

@app.route('/webhook/case3', methods=['POST'])
def handle_case3():
    """케이스3 실행버튼 처리"""
    data = request.json
    target = data.get('target', 'Z062')
    
    # 케이스3 실행
    result = subprocess.run([
        'python', 'scripts/run_notion_workflow.py',
        '--case', '3',
        '--target', target, 
        '--out', f'logs/webhook_case3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    ], capture_output=True, text=True)
    
    # Notion 페이지 업데이트
    update_notion_page(data['notion_page_id'], {
        'status': 'success' if result.returncode == 0 else 'failed',
        'message': '케이스3 실행 완료',
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'status': 'success'})

def update_notion_page(page_id, result):
    """Notion 페이지에 실행 결과 업데이트"""
    # 기존 Notion API 클라이언트 사용
    from src.utils.notion_api import NotionClient
    import os
    
    client = NotionClient(os.environ.get("NOTION_TOKEN"))
    
    # 페이지에 실행 결과 추가
    properties = {
        "실행 상태": {
            "select": {
                "name": result['status']
            }
        },
        "실행 메시지": {
            "rich_text": [
                {
                    "text": {
                        "content": result['message']
                    }
                }
            ]
        },
        "실행 시간": {
            "date": {
                "start": result['timestamp']
            }
        }
    }
    
    client._req("PATCH", f"/pages/{page_id}", json={"properties": properties})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
```

### **2. 실행버튼 전용 스크립트**

```python
# scripts/notion_button_handler.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 실행버튼 전용 핸들러
목적: 웹훅 요청을 받아서 해당 케이스 실행 및 결과 반환
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workflows.notion_collaboration import NotionCollaborationWorkflow

def handle_case1(target="Z062", notion_page_id=None):
    """케이스1 실행버튼 처리"""
    print(f"🔧 케이스1 실행버튼 처리: {target}")
    
    workflow = NotionCollaborationWorkflow()
    result = workflow.case1_handshake()
    
    # Notion 페이지 업데이트
    if notion_page_id:
        update_notion_result(notion_page_id, "케이스1", result)
    
    return result

def handle_case2(target="Z062", notion_page_id=None):
    """케이스2 실행버튼 처리"""
    print(f"🔧 케이스2 실행버튼 처리: {target}")
    
    workflow = NotionCollaborationWorkflow()
    result = workflow.case2_page_identification(target)
    
    # Notion 페이지 업데이트
    if notion_page_id:
        update_notion_result(notion_page_id, "케이스2", result)
    
    return result

def handle_case3(target="Z062", notion_page_id=None):
    """케이스3 실행버튼 처리"""
    print(f"🔧 케이스3 실행버튼 처리: {target}")
    
    workflow = NotionCollaborationWorkflow()
    news_data = {
        "title": f"[실행버튼] {target} 관련 뉴스 등록",
        "url": f"https://example.com/{target.lower()}-news",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "실행버튼 매체",
        "category": "해상풍력발전",
        "importance": "보통"
    }
    result = workflow.case3_news_registration(news_data)
    
    # Notion 페이지 업데이트
    if notion_page_id:
        update_notion_result(notion_page_id, "케이스3", result)
    
    return result

def update_notion_result(notion_page_id, case_name, result):
    """Notion 페이지에 실행 결과 업데이트"""
    from src.utils.notion_api import NotionClient
    import os
    
    try:
        client = NotionClient(os.environ.get("NOTION_TOKEN"))
        
        # 실행 결과를 페이지에 추가
        status = "성공" if result.get('overall_status') == 'success' else "실패"
        message = f"{case_name} 실행 {status}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 페이지 속성 업데이트
        properties = {
            "실행 상태": {
                "select": {"name": status}
            },
            "실행 메시지": {
                "rich_text": [{"text": {"content": message}}]
            },
            "실행 시간": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
        
        client._req("PATCH", f"/pages/{notion_page_id}", json={"properties": properties})
        print(f"✅ Notion 페이지 업데이트 완료: {notion_page_id}")
        
    except Exception as e:
        print(f"❌ Notion 페이지 업데이트 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description="Notion 실행버튼 핸들러")
    parser.add_argument("--case", choices=["1", "2", "3"], required=True, help="실행할 케이스")
    parser.add_argument("--target", default="Z062", help="대상 키워드")
    parser.add_argument("--notion-page-id", help="Notion 페이지 ID")
    args = parser.parse_args()
    
    if args.case == "1":
        result = handle_case1(args.target, args.notion_page_id)
    elif args.case == "2":
        result = handle_case2(args.target, args.notion_page_id)
    elif args.case == "3":
        result = handle_case3(args.target, args.notion_page_id)
    
    print(f"📊 실행 결과: {result.get('overall_status', 'unknown')}")
    return 0 if result.get('overall_status') == 'success' else 1

if __name__ == "__main__":
    exit(main())
```

## 🎯 **선과장님께 제안사항**

### **1. Notion Automation 설정**

#### **A. 실행버튼 생성**
```
ZOBIS 실행 대시보드 페이지에 다음 버튼들을 생성:

1. [🔧 케이스1 실행] 버튼
   - 웹훅 URL: http://localhost:8000/webhook/case1
   - 페이로드: {"case": "case1", "target": "Z062", "notion_page_id": "{{page_id}}"}

2. [🔧 케이스2 실행] 버튼  
   - 웹훅 URL: http://localhost:8000/webhook/case2
   - 페이로드: {"case": "case2", "target": "Z062", "notion_page_id": "{{page_id}}"}

3. [🔧 케이스3 실행] 버튼
   - 웹훅 URL: http://localhost:8000/webhook/case3  
   - 페이로드: {"case": "case3", "target": "Z062", "notion_page_id": "{{page_id}}"}

4. [🚀 전체 실행] 버튼
   - 웹훅 URL: http://localhost:8000/webhook/all
   - 페이로드: {"case": "all", "target": "Z062", "notion_page_id": "{{page_id}}"}
```

#### **B. 결과 표시 영역**
```
실행 결과를 표시할 속성들:

- 실행 상태 (select): 성공/실패/진행중
- 실행 메시지 (rich_text): 실행 결과 메시지
- 실행 시간 (date): 마지막 실행 시간
- 실행 로그 (rich_text): 상세 실행 로그
```

### **2. 서대리 시스템 준비**

#### **A. 웹훅 서버 실행**
```bash
# 웹훅 서버 실행 (로컬)
python webhook_server.py

# 또는 실행버튼 전용 핸들러 사용
python scripts/notion_button_handler.py --case 1 --target Z062 --notion-page-id <page_id>
```

#### **B. 환경 설정**
```bash
# 필요한 패키지 설치
pip install flask requests

# 환경변수 설정 (config.env)
NOTION_TOKEN=ntn_...
TARGET_DATABASE_ID=...
```

### **3. 운영 시나리오**

#### **시나리오 1: 개별 케이스 실행**
1. 조대표님이 Notion에서 "[🔧 케이스1 실행]" 버튼 클릭
2. Notion Automation이 웹훅으로 서대리 시스템 호출
3. 서대리 시스템이 케이스1 실행
4. 실행 결과를 Notion 페이지에 자동 업데이트

#### **시나리오 2: 전체 워크플로우 실행**
1. 조대표님이 Notion에서 "[🚀 전체 실행]" 버튼 클릭
2. 서대리 시스템이 케이스1+2+3 순차 실행
3. 각 단계별 결과를 Notion에 실시간 업데이트

## 🚀 **구현 우선순위**

### **Phase 1: 기본 실행버튼 (1주)**
- 케이스1,2,3 개별 실행버튼 구현
- 기본 웹훅 연동
- 결과 표시 기능

### **Phase 2: 고도화 (2주)**
- 전체 워크플로우 실행버튼
- 실시간 진행상황 표시
- 에러 처리 및 재시도 기능

### **Phase 3: 자동화 (3주)**
- 스케줄링 기능
- 배치 처리 기능
- 모니터링 대시보드

## 📋 **선과장님께 요청사항**

1. **Notion Automation 설정**: 위의 실행버튼들을 ZOBIS 대시보드에 생성
2. **웹훅 URL 확인**: 서대리 시스템의 웹훅 서버 URL 확인
3. **결과 표시 영역**: 실행 결과를 표시할 속성들 설정
4. **테스트 환경**: 개발 환경에서 실행버튼 테스트

**조대표님, 이 방안으로 Notion에서 원클릭으로 CASE1,2,3을 실행할 수 있게 됩니다!** 🎉
