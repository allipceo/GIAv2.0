import os
import re
import json
import datetime
import subprocess
import logging
from pathlib import Path

try:
    from radon.complexity import cc_visit
except ImportError:
    cc_visit = None
    print("[WARN] radon 라이브러리가 설치되어 있지 않습니다. 복잡도 분석이 제한됩니다.")

# === 설정 ===
REPO_ROOT = os.path.join(os.getcwd(), 'GLOBAL_CODE_REPO')
SCAN_BRANCH = 'main'
LOG_FILE = os.path.join(REPO_ROOT, 'scanner.log')
ONBOARDING_FILE = os.path.join(REPO_ROOT, 'onboarding.md')

# === 로깅 설정 ===
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def extract_snippets(file_path):
    """# GI_SNIPPET 블록 또는 함수/클래스 단위 스니펫 추출"""
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    snippets = []
    # 1. # GI_SNIPPET 블록
    gi_blocks = re.findall(r'# GI_SNIPPET(.*?)# /GI_SNIPPET', code, re.DOTALL)
    for block in gi_blocks:
        snippets.append(block.strip())
    # 2. 함수/클래스 정의 + 첫 20줄
    if not snippets:
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(('def ', 'class ')):
                snippet = '\n'.join(lines[i:i+20])
                snippets.append(snippet)
    return snippets

def calc_quality_metrics(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    length = len(code.splitlines())
    function_count = len(re.findall(r'^def ', code, re.MULTILINE))
    import_count = len(re.findall(r'^import |^from ', code, re.MULTILINE))
    complexity = 0
    if cc_visit:
        try:
            complexity = sum([block.complexity for block in cc_visit(code)])
        except Exception:
            complexity = -1
    return {
        'length': length,
        'function_count': function_count,
        'import_count': import_count,
        'cyclomatic_complexity': complexity
    }

def get_git_diff(file_path):
    rel_path = os.path.relpath(file_path, REPO_ROOT)
    try:
        result = subprocess.run(['git', '-C', REPO_ROOT, 'diff', 'HEAD', rel_path], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"[ERROR] git diff 실패: {e}"

def save_snippet_and_metadata(file_path, snippets, quality_metrics):
    meta = {
        'file_name': os.path.basename(file_path),
        'snippets': snippets,
        'quality_metrics': quality_metrics,
        'manual_metrics': {
            'reusability': '',
            'business_importance': '',
            'difficulty': ''
        },
        'tags': [],
        'history': [],
        'file_link': os.path.relpath(file_path, REPO_ROOT),
        'unique_id': f"{os.path.basename(file_path)}_{int(datetime.datetime.now().timestamp())}"
    }
    meta_path = file_path + '.metadata.json'
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    logging.info(f"메타데이터 저장: {meta_path}")

def scan_repository():
    features_dir = os.path.join(REPO_ROOT, SCAN_BRANCH, 'features')
    for root, _, files in os.walk(features_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    snippets = extract_snippets(file_path)
                    quality_metrics = calc_quality_metrics(file_path)
                    save_snippet_and_metadata(file_path, snippets, quality_metrics)
                    diff = get_git_diff(file_path)
                    if diff:
                        logging.info(f"git diff for {file}:\n{diff}")
                except Exception as e:
                    logging.error(f"[ERROR] {file_path}: {e}")
                    print(f"[ERROR] {file_path}: {e}")

def create_onboarding_guide():
    guide = """
# 신규 멤버 온보딩 가이드

1. GLOBAL_CODE_REPO 폴더 구조와 파일명 규칙 숙지
2. 코드 추가 시 .metadata.json 자동 생성 확인
3. 품질 지표(자동/수동) 입력 및 태그/분류 체계 준수
4. git 커밋/푸시 및 변경 이력 관리
5. 오류/이슈 발생시 scanner.log 및 README.md 참고
"""
    with open(ONBOARDING_FILE, 'w', encoding='utf-8') as f:
        f.write(guide)
    print(f"[INFO] 온보딩 가이드 생성: {ONBOARDING_FILE}")

def create_scheduler_bat():
    bat_path = os.path.join(REPO_ROOT, 'run_scanner_hourly.bat')
    py_path = os.path.abspath(__file__)
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(f'@echo off\npython "{py_path}"\n')
    print(f"[INFO] 스케줄러용 .bat 파일 생성: {bat_path}")

def main():
    logging.info("=== Intelligent Code Scanner 시작 ===")
    scan_repository()
    create_onboarding_guide()
    create_scheduler_bat()
    logging.info("=== Intelligent Code Scanner 종료 ===")
    print("[SUCCESS] create_intelligent_code_scanner.py 실행 완료!")

if __name__ == "__main__":
    main() 