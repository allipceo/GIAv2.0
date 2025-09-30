import os
import uuid
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from utils.notion_api import (
    check_health,
    get_database_schema,
    extract_status_property_id,
    get_page,
    validate_page_in_database,
    set_status_by_property_id,
    NotionApiError,
)


def _get_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def step_health_check() -> Dict[str, Any]:
    url = _get_env("G2N_HEALTH_URL")
    return check_health(url)


def step_fetch_status_property_id() -> str:
    token = _get_env("NOTION_TOKEN")
    dbid = _get_env("TARGET_DATABASE_ID")
    schema = get_database_schema(token, dbid)
    return extract_status_property_id(schema)


def _ensure_page_in_db(page_id: str, target_db: str):
    token = _get_env("NOTION_TOKEN")
    pj = get_page(token, page_id)
    if not validate_page_in_database(pj, target_db):
        raise NotionApiError("Page is not a child of TARGET_DATABASE_ID")


def run_g1_regression(status_property_id: str) -> List[Dict[str, Any]]:
    token = _get_env("NOTION_TOKEN")
    dbid = _get_env("TARGET_DATABASE_ID")
    page_id = _get_env("Z062_PAGE_ID")

    _ensure_page_in_db(page_id, dbid)

    scenarios = ["작성중", "검토중", "작성중"]
    logs: List[Dict[str, Any]] = []

    for status_name in scenarios:
        trace_id = f"g1_{uuid.uuid4().hex[:8]}"
        started = time.time()
        payload_summary = {status_property_id: {"status": {"name": status_name}}}
        try:
            res = set_status_by_property_id(token, page_id, status_property_id, status_name, parent_database_id=dbid)
            code = 200
        except Exception as e:
            res = {"error": str(e)}
            code = 500
        duration_ms = int((time.time() - started) * 1000)
        logs.append(
            {
                "trace_id": trace_id,
                "page_id": page_id,
                "database_id": dbid,
                "property_id": status_property_id,
                "payload": payload_summary,
                "response_code": code,
                "duration_ms": duration_ms,
            }
        )

    return logs


def _update_status_job(args: Dict[str, Any]) -> Dict[str, Any]:
    token = args["token"]
    dbid = args["dbid"]
    page_id = args["page_id"]
    status_property_id = args["status_property_id"]
    status_name = args["status_name"]
    trace_id = args["trace_id"]

    started = time.time()
    payload_summary = {status_property_id: {"status": {"name": status_name}}}
    try:
        _ = set_status_by_property_id(token, page_id, status_property_id, status_name, parent_database_id=dbid)
        code = 200
        err = None
    except Exception as e:
        code = 500
        err = str(e)
    duration_ms = int((time.time() - started) * 1000)
    return {
        "trace_id": trace_id,
        "page_id": page_id,
        "database_id": dbid,
        "property_id": status_property_id,
        "payload": payload_summary,
        "response_code": code,
        "duration_ms": duration_ms,
        "error": err,
    }


def run_g2_batch(status_property_id: str, page_ids: List[str], status_name: str = "검토중", concurrency: int = 3) -> Dict[str, Any]:
    token = _get_env("NOTION_TOKEN")
    dbid = _get_env("TARGET_DATABASE_ID")

    # Pre-validate page parents
    for pid in page_ids:
        _ensure_page_in_db(pid, dbid)

    jobs: List[Dict[str, Any]] = []
    for pid in page_ids:
        jobs.append(
            {
                "token": token,
                "dbid": dbid,
                "page_id": pid,
                "status_property_id": status_property_id,
                "status_name": status_name,
                "trace_id": f"g2_{uuid.uuid4().hex[:8]}",
            }
        )

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = [ex.submit(_update_status_job, j) for j in jobs]
        for fut in as_completed(futs):
            results.append(fut.result())

    # basic report
    success = sum(1 for r in results if r["response_code"] // 100 == 2)
    fail = len(results) - success
    avg_ms = int(sum(r["duration_ms"] for r in results) / max(1, len(results)))
    results_sorted = sorted(results, key=lambda r: r["response_code"])
    top_fail = [r for r in results_sorted if r["response_code"] >= 400][:3]
    return {
        "total": len(results),
        "success": success,
        "fail": fail,
        "avg_duration_ms": avg_ms,
        "top_fail": top_fail,
        "results": results,
    }

# D:\AI_Project\GIAv2.0\src\branch_manager.py

import subprocess
import os

def get_current_git_branch(repo_path):
    """
    주어진 경로의 Git 저장소에서 현재 활성화된 브랜치 이름을 가져옵니다.

    Args:
        repo_path (str): Git 저장소의 경로.

    Returns:
        str: 현재 브랜치 이름 또는 오류 발생 시 None.
    """
    try:
        # Git 명령어를 실행하여 현재 브랜치 이름을 가져옵니다.
        # 'git rev-parse --abbrev-ref HEAD'는 현재 브랜치의 짧은 이름을 반환합니다.
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=repo_path, # 명령어를 실행할 디렉토리 설정
            capture_output=True,
            text=True,
            check=True # 0이 아닌 종료 코드를 반환하면 CalledProcessError 발생
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git 명령어 실행 오류: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Git 실행 파일을 찾을 수 없습니다. Git이 설치되어 있고 PATH에 추가되었는지 확인하세요.")
        return None
    except Exception as e:
        print(f"브랜치 정보를 가져오는 중 예상치 못한 오류 발생: {e}")
        return None

def check_branch_safety(repo_path, expected_branch):
    """
    현재 Git 브랜치가 예상 브랜치와 일치하는지 확인하여 안전 장치 역할을 합니다.

    Args:
        repo_path (str): Git 저장소의 경로.
        expected_branch (str): 예상되는 브랜치 이름.

    Returns:
        bool: 현재 브랜치가 예상 브랜치와 일치하면 True, 그렇지 않으면 False.
    """
    current_branch = get_current_git_branch(repo_path)

    if current_branch is None:
        print("경고: 현재 Git 브랜치를 확인할 수 없습니다. 작업 진행에 주의하세요.")
        return False
    elif current_branch == expected_branch:
        print(f"정보: 현재 브랜치 '{current_branch}'가 예상 브랜치 '{expected_branch}'와 일치합니다. 안전하게 작업을 진행할 수 있습니다.")
        return True
    else:
        print(f"경고: 현재 브랜치 '{current_branch}'가 예상 브랜치 '{expected_branch}'와 다릅니다.")
        print("  작업을 계속하기 전에 올바른 브랜치로 전환하거나, 이 상황이 의도된 것인지 확인하세요.")
        return False

# 이 스크립트가 직접 실행될 경우를 위한 예시
if __name__ == "__main__":
    # 서대리의 작업 환경에 맞춰 D:\AI_Project\GIAv2.0 경로를 사용합니다.
    project_repo_path = "D:\\AI_Project\\GIAv2.0"
    expected_feature_branch = "gia-feature-infosys1" # 서대리가 작업할 브랜치

    print(f"Git 저장소 경로: {project_repo_path}")
    print(f"예상 브랜치: {expected_feature_branch}")

    # 브랜치 안전성 확인
    if check_branch_safety(project_repo_path, expected_feature_branch):
        print("\n브랜치 확인 완료. 다음 작업을 시작할 수 있습니다.")
    else:
        print("\n브랜치 불일치 또는 확인 불가. 작업 진행 전 조치 필요.")
