import os
import json
from datetime import datetime

def verify_backup_files():
    """백업 파일 검증"""
    print("🔍 백업 파일 검증 시작")
    print("=" * 50)
    
    backup_dir = "backups/phase0_20250719_2310"
    expected_files = [
        "기업 위험 프로파일_backup.json",
        "글로벌 경쟁 분석_backup.json", 
        "재무 및 프로젝트_backup.json",
        "태스크 관리_backup.json",
        "코드 관리_backup.json",
        "뉴스 정보_backup.json"
    ]
    
    success_count = 0
    total_count = len(expected_files)
    
    for filename in expected_files:
        filepath = os.path.join(backup_dir, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    record_count = len(data.get('results', []))
                    print(f"✅ {filename}: {record_count}개 레코드")
                    success_count += 1
            except Exception as e:
                print(f"❌ {filename}: 파일 읽기 오류 - {e}")
        else:
            print(f"❌ {filename}: 파일 없음")
    
    print("=" * 50)
    print(f"📊 검증 완료: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("✅ 모든 백업 파일 검증 성공")
        return True
    else:
        print("❌ 일부 백업 파일 검증 실패")
        return False

if __name__ == "__main__":
    verify_backup_files() 