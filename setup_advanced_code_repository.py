import os
import json
import datetime
import subprocess

# === 설정 ===
REPO_ROOT = os.path.join(os.getcwd(), 'GLOBAL_CODE_REPO')
BRANCH_NAME = 'main'  # 실제 브랜치명 자동 감지로 확장 가능
FOLDER_STRUCTURE = [
    os.path.join(REPO_ROOT, BRANCH_NAME, 'features'),
    os.path.join(REPO_ROOT, BRANCH_NAME, 'archive'),
]
METADATA_TEMPLATE = {
    "file_name": "",
    "created_at": "",
    "author": "",
    "quality_metrics": {
        "length": 0,
        "function_count": 0,
        "import_count": 0,
        "cyclomatic_complexity": 0
    },
    "manual_metrics": {
        "reusability": "",
        "business_importance": "",
        "difficulty": ""
    },
    "tags": [],
    "history": []
}

README_TEMPLATE = """
# GLOBAL_CODE_REPO 운영 매뉴얼

## 폴더 구조
- main/features: 기능별 코드 저장
- main/archive: 아카이브(이전 버전, 백업 등)

## 파일명 규칙
- YYYYMMDD_기능명_vX.Y.py (예: 20250706_setup_code_repo_v1.0.py)

## 메타데이터 관리
- 각 코드 파일별 .metadata.json 자동 생성 및 관리

## git 연동
- 변경사항은 반드시 커밋/푸시
- git diff 기반 변경 이력 자동 기록

## 신규 멤버 온보딩
- 이 매뉴얼을 참고하여 폴더/파일/메타데이터 규칙을 준수
"""

MANUAL_FILE = os.path.join(REPO_ROOT, 'README.md')

# === 함수 정의 ===
def create_folder_structure():
    for folder in FOLDER_STRUCTURE:
        os.makedirs(folder, exist_ok=True)
    print(f"[INFO] 폴더 구조 생성 완료: {FOLDER_STRUCTURE}")

def create_sample_file():
    today = datetime.datetime.now().strftime('%Y%m%d')
    sample_name = f"{today}_setup_code_repo_v1.0.py"
    sample_path = os.path.join(REPO_ROOT, BRANCH_NAME, 'features', sample_name)
    with open(sample_path, 'w', encoding='utf-8') as f:
        f.write("""# 샘플 코드 파일\nprint('Hello, GLOBAL_CODE_REPO!')\n""")
    print(f"[INFO] 샘플 파일 생성: {sample_path}")
    return sample_path

def create_metadata_for_file(file_path):
    meta = METADATA_TEMPLATE.copy()
    meta['file_name'] = os.path.basename(file_path)
    meta['created_at'] = datetime.datetime.now().isoformat()
    meta_path = file_path + '.metadata.json'
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"[INFO] 메타데이터 파일 생성: {meta_path}")

def init_git_repo():
    if not os.path.exists(os.path.join(REPO_ROOT, '.git')):
        subprocess.run(['git', 'init'], cwd=REPO_ROOT)
        with open(os.path.join(REPO_ROOT, '.gitignore'), 'w', encoding='utf-8') as f:
            f.write("*.pyc\n__pycache__/\n.DS_Store\n")
        print("[INFO] git 저장소 초기화 및 .gitignore 생성 완료")
    else:
        print("[INFO] 이미 git 저장소가 초기화되어 있습니다.")

def create_manual():
    with open(MANUAL_FILE, 'w', encoding='utf-8') as f:
        f.write(README_TEMPLATE)
    print(f"[INFO] 운영 매뉴얼(README.md) 생성: {MANUAL_FILE}")

# === 실행 ===
if __name__ == "__main__":
    create_folder_structure()
    sample_file = create_sample_file()
    create_metadata_for_file(sample_file)
    init_git_repo()
    create_manual()
    print("[SUCCESS] setup_advanced_code_repository.py 실행 완료!") 