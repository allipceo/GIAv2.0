#!/usr/bin/env python3
"""
민감한 정보 제거 스크립트
- 하드코딩된 API 키, 토큰 제거
- 환경변수로 대체
"""

import os
import re
from pathlib import Path

def remove_sensitive_data():
    """하드코딩된 민감한 정보 제거"""
    
    # 제거할 민감한 정보 패턴
    sensitive_patterns = [
        r'',
        r'NOTION_TOKEN\s*=\s*["\'][^"\']+["\']',
        r'CSE_API_KEY\s*=\s*["\'][^"\']+["\']',
        r'GOOGLE_CUSTOM_SEARCH_API_KEY\s*=\s*["\'][^"\']+["\']',
        r'NAVER_CLIENT_ID\s*=\s*["\'][^"\']+["\']',
        r'NAVER_CLIENT_SECRET\s*=\s*["\'][^"\']+["\']',
    ]
    
    # 제외할 파일들 (핵심 파일)
    exclude_files = {
        'src/utils/web_search_adapter.py',
        'src/utils/notion_api.py',
        'scripts/a2g2n_collect_only.py',
        'scripts/a2g2n_register_from_temp.py',
        'scripts/smoke_cse_test.py',
        'scripts/notion_probe_and_register.py',
        'docs/',
        'config.env'
    }
    
    # 처리할 파일 확장자
    file_extensions = ['.py', '.md', '.txt', '.json']
    
    removed_count = 0
    
    for root, dirs, files in os.walk('.'):
        # 제외할 디렉토리 스킵
        if any(exclude in root for exclude in ['__pycache__', '.git', 'node_modules']):
            continue
            
        for file in files:
            file_path = Path(root) / file
            
            # 제외할 파일 스킵
            if str(file_path) in exclude_files:
                continue
                
            # 파일 확장자 확인
            if not any(file.endswith(ext) for ext in file_extensions):
                continue
                
            try:
                # 파일 읽기
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # 민감한 정보 제거
                for pattern in sensitive_patterns:
                    content = re.sub(pattern, '', content, flags=re.IGNORECASE)
                
                # 변경사항이 있으면 파일 저장
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    removed_count += 1
                    print(f"민감한 정보 제거: {file_path}")
                    
            except Exception as e:
                print(f"처리 실패: {file_path} - {e}")
    
    print(f"총 {removed_count}개 파일에서 민감한 정보 제거 완료")
    return removed_count

if __name__ == "__main__":
    print("민감한 정보 제거 작업 시작...")
    removed_count = remove_sensitive_data()
    print(f"민감한 정보 제거 완료: {removed_count}개 파일")
