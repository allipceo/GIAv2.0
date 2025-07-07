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
