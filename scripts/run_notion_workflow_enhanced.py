#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
확장된 Notion 워크플로우 실행 스크립트
목적: 선과장님 지침에 따른 가드 체인, 보안, 출력 표준화 구현
"""

import os
import sys
import json
import argparse
import hmac
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workflows.notion_collaboration import NotionCollaborationWorkflow
from src.utils.notion_api import NotionClient

class SecurityError(Exception):
    """보안 관련 오류"""
    pass

class GuardError(Exception):
    """가드 체인 오류"""
    pass

class SchemaMismatchError(Exception):
    """스키마 불일치 오류"""
    pass

class NonceReuseError(Exception):
    """nonce 재사용 오류"""
    pass

class TimestampExpiredError(Exception):
    """타임스탬프 만료 오류"""
    pass

class InvalidSignatureError(Exception):
    """잘못된 서명 오류"""
    pass

class EnhancedNotionWorkflow:
    """확장된 Notion 워크플로우 클래스"""
    
    def __init__(self, config_file: str = "config.env"):
        """워크플로우 초기화"""
        load_dotenv(config_file)
        self.token = os.environ.get("NOTION_TOKEN")
        self.client = NotionClient(self.token) if self.token else None
        self.nonce_manager = NonceManager()
        self.secret_key = os.environ.get("WEBHOOK_SECRET_KEY", "default_secret_key")
        
    def validate_input_schema(self, data: Dict[str, Any]) -> bool:
        """입력 스키마 검증"""
        required_fields = ["case", "mode", "ts", "nonce"]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # 케이스 검증
        if data["case"] not in ["1", "2", "3", "all"]:
            raise ValueError("Invalid case value")
        
        # 모드 검증
        if data["mode"] not in ["dryrun", "apply"]:
            raise ValueError("Invalid mode value")
        
        return True
    
    def validate_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """HMAC-SHA256 서명 검증"""
        # 1. 타임스탬프 유효성 검증 (5분)
        current_time = int(time.time())
        if abs(current_time - payload.get('ts', 0)) > 300:
            raise TimestampExpiredError("Timestamp expired")
        
        # 2. nonce 재사용 차단
        nonce = payload.get('nonce')
        if self.nonce_manager.is_nonce_used(nonce):
            raise NonceReuseError("Nonce already used")
        
        # 3. 서명 검증
        expected_sig = hmac.new(
            self.secret_key.encode(),
            json.dumps(payload, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            raise InvalidSignatureError("Invalid signature")
        
        # 4. nonce 사용 표시
        self.nonce_manager.mark_nonce_used(nonce)
        
        return True
    
    def validate_guard_chain(self, db_id: str, page_id: Optional[str] = None) -> bool:
        """가드 체인 검증"""
        try:
            # 1. users/me, databases = 200
            user_info = self.client.users_me()
            db_info = self.client.get_database(db_id)
            
            if not user_info or not db_info:
                raise GuardError("Failed to access Notion API")
            
            # 2. parent.database_id, page 소속 검증
            if page_id:
                page_info = self.client.get_page(page_id)
                if not self._validate_page_in_database(page_info, db_id):
                    raise GuardError("Page does not belong to specified database")
            
            # 3. schema_hash 일치 시 쓰기 허용
            current_hash = self._build_schema_hash(db_info)
            cached_hash = self._load_schema_hash()
            if current_hash != cached_hash:
                raise SchemaMismatchError("Schema hash mismatch")
            
            # 4. 옵션 화이트리스트 검증
            self._validate_whitelist_options(db_info)
            
            return True
            
        except Exception as e:
            raise GuardError(f"Guard chain validation failed: {e}")
    
    def _validate_page_in_database(self, page_info: Dict[str, Any], db_id: str) -> bool:
        """페이지가 데이터베이스에 속하는지 검증"""
        parent = page_info.get("parent", {})
        return parent.get("database_id") == db_id
    
    def _build_schema_hash(self, db_info: Dict[str, Any]) -> str:
        """스키마 해시 생성"""
        properties = db_info.get("properties", {})
        sig = {k: {"id": v.get("id"), "type": v.get("type")} for k, v in properties.items()}
        raw = json.dumps(sig, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
    
    def _load_schema_hash(self) -> str:
        """캐시된 스키마 해시 로드"""
        try:
            with open(".schema_hash.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""
    
    def _validate_whitelist_options(self, db_info: Dict[str, Any]) -> bool:
        """화이트리스트 옵션 검증"""
        properties = db_info.get("properties", {})
        
        # 상태 옵션 검증
        if "상태" in properties:
            status_options = properties["상태"].get("select", {}).get("options", [])
            self._validate_status_options(status_options)
        
        # 태그 옵션 검증
        if "태그" in properties:
            tag_options = properties["태그"].get("multi_select", {}).get("options", [])
            self._validate_tag_options(tag_options)
        
        # 중요도 옵션 검증
        if "중요도" in properties:
            importance_options = properties["중요도"].get("select", {}).get("options", [])
            self._validate_importance_options(importance_options)
        
        return True
    
    def _validate_status_options(self, options: list) -> bool:
        """상태 옵션 검증"""
        valid_statuses = ["작성중", "완료", "검토중", "보류"]
        for option in options:
            if option.get("name") not in valid_statuses:
                raise GuardError(f"Invalid status option: {option.get('name')}")
        return True
    
    def _validate_tag_options(self, options: list) -> bool:
        """태그 옵션 검증"""
        valid_tags = ["해상풍력발전", "방산", "에너지", "기술"]
        for option in options:
            if option.get("name") not in valid_tags:
                raise GuardError(f"Invalid tag option: {option.get('name')}")
        return True
    
    def _validate_importance_options(self, options: list) -> bool:
        """중요도 옵션 검증"""
        valid_importance = ["매우중요", "중요", "보통", "무시"]
        for option in options:
            if option.get("name") not in valid_importance:
                raise GuardError(f"Invalid importance option: {option.get('name')}")
        return True
    
    def generate_standard_log(self, case: str, page_id: str, db_id: str, result: Dict[str, Any]) -> str:
        """표준 로그 생성"""
        timestamp = int(time.time())
        log_filename = f"logs/{case}*{page_id or db_id}*{timestamp}.md"
        
        log_content = f"""# {case} 실행 결과

**실행 시간**: {datetime.fromtimestamp(timestamp).isoformat()}
**대상**: {page_id or db_id}
**결과**: {result.get('overall_status', 'unknown')}

## 실행 단계
{self._format_execution_steps(result.get('steps', []))}

## 결과 요약
{result.get('summary', 'N/A')}

## 에러 정보
{result.get('error', 'N/A')}
"""
        
        os.makedirs("logs", exist_ok=True)
        with open(log_filename, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        return log_filename
    
    def _format_execution_steps(self, steps: list) -> str:
        """실행 단계 포맷팅"""
        formatted_steps = []
        for i, step in enumerate(steps, 1):
            status = step.get('status', 'unknown')
            message = step.get('message', 'N/A')
            formatted_steps.append(f"{i}. {status}: {message}")
        return "\n".join(formatted_steps)
    
    def attach_summary_hook(self, target_page_id: str, log_file_path: str, case: str):
        """summary 자동 첨부 훅"""
        try:
            if case == "2":
                # 케이스2: "### 개발결과" 앵커 하단에 3줄 요약 + 근거 링크
                self._attach_to_development_results(target_page_id, log_file_path)
            elif case == "3":
                # 케이스3: Z072 "케이스 3 결과 링크"에 항목 링크 추가
                self._attach_to_case3_results(target_page_id, log_file_path)
            else:
                # 공통: summary 링크를 대상 페이지 또는 Z072 하단에 자동 첨부
                self._attach_to_general_results(target_page_id, log_file_path)
        except Exception as e:
            print(f"❌ Summary hook attachment failed: {e}")
    
    def _attach_to_development_results(self, page_id: str, log_file_path: str):
        """개발결과 섹션에 첨부"""
        # 구현 필요
        pass
    
    def _attach_to_case3_results(self, page_id: str, log_file_path: str):
        """케이스3 결과에 첨부"""
        # 구현 필요
        pass
    
    def _attach_to_general_results(self, page_id: str, log_file_path: str):
        """일반 결과에 첨부"""
        # 구현 필요
        pass

class NonceManager:
    """nonce 관리 클래스"""
    
    def __init__(self):
        self.used_nonces = set()
        self.cleanup_interval = 3600  # 1시간
    
    def is_nonce_used(self, nonce: str) -> bool:
        """nonce 재사용 확인"""
        return nonce in self.used_nonces
    
    def mark_nonce_used(self, nonce: str):
        """nonce 사용 표시"""
        self.used_nonces.add(nonce)
    
    def cleanup_expired_nonces(self):
        """만료된 nonce 정리"""
        # 구현 필요
        pass

def main():
    parser = argparse.ArgumentParser(description="확장된 Notion 워크플로우 실행")
    parser.add_argument("--case", choices=["1", "2", "3", "all"], required=True, help="실행할 케이스")
    parser.add_argument("--target", help="대상 키워드")
    parser.add_argument("--page-id", help="페이지 ID")
    parser.add_argument("--db-id", help="데이터베이스 ID")
    parser.add_argument("--mode", choices=["dryrun", "apply"], default="dryrun", help="실행 모드")
    parser.add_argument("--guard", default="config/rules/g0_guard.json", help="가드 규칙 파일")
    parser.add_argument("--schema-cache", default=".schema_hash.txt", help="스키마 캐시 파일")
    parser.add_argument("--signature", help="HMAC 서명")
    parser.add_argument("--timestamp", type=int, help="타임스탬프")
    parser.add_argument("--nonce", help="nonce")
    args = parser.parse_args()
    
    print("🚀 확장된 Notion 워크플로우 실행 시작...")
    print(f"케이스: {args.case}")
    print(f"모드: {args.mode}")
    print(f"대상: {args.target or args.page_id}")
    
    try:
        # 워크플로우 초기화
        workflow = EnhancedNotionWorkflow()
        
        if not workflow.client:
            print("❌ NotionClient 초기화 실패")
            return 1
        
        # 입력 스키마 검증
        input_data = {
            "case": args.case,
            "mode": args.mode,
            "ts": args.timestamp or int(time.time()),
            "nonce": args.nonce or "default_nonce"
        }
        
        workflow.validate_input_schema(input_data)
        
        # 서명 검증 (apply 모드에서만)
        if args.mode == "apply" and args.signature:
            workflow.validate_signature(input_data, args.signature)
        
        # 가드 체인 검증
        target_db_id = args.db_id or os.environ.get("TARGET_DATABASE_ID")
        if not target_db_id:
            print("❌ 데이터베이스 ID가 지정되지 않았습니다")
            return 1
        
        workflow.validate_guard_chain(target_db_id, args.page_id)
        
        # 케이스 실행
        if args.case == "1":
            result = workflow.client.case1_handshake()
        elif args.case == "2":
            result = workflow.client.case2_page_identification(args.target or "Z062")
        elif args.case == "3":
            news_data = {
                "title": f"[{args.mode}] {args.target or 'Z062'} 관련 뉴스 등록",
                "url": f"https://example.com/{args.target or 'Z062'}-news",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "실행버튼 매체",
                "category": "해상풍력발전",
                "importance": "보통"
            }
            result = workflow.client.case3_news_registration(news_data)
        else:  # all
            result = workflow.client.run_full_workflow(args.target or "Z062")
        
        # 표준 로그 생성
        log_file = workflow.generate_standard_log(
            args.case, 
            args.page_id or "", 
            target_db_id, 
            result
        )
        
        # summary 자동 첨부 훅
        if args.mode == "apply":
            workflow.attach_summary_hook(
                args.page_id or target_db_id, 
                log_file, 
                args.case
            )
        
        print(f"✅ {args.case} 실행 완료: {result.get('overall_status', 'unknown')}")
        print(f"📁 로그 파일: {log_file}")
        
        return 0 if result.get('overall_status') == 'success' else 1
        
    except (SecurityError, GuardError, SchemaMismatchError, NonceReuseError, 
            TimestampExpiredError, InvalidSignatureError) as e:
        print(f"❌ 보안/가드 오류: {e}")
        return 1
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
