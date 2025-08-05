# D:\AI_Project\GIAv2.0\src\project_setup.py

import os

def create_project_structure(base_path):
    """
    GI-AGENT 정보수집체계 프로젝트의 기본 폴더 구조를 생성합니다.
    이미 존재하는 폴더는 건너뜁니다.

    Args:
        base_path (str): 프로젝트의 기본 경로 (예: D:\AI_Project\GIAv2.0)
    """
    print(f"프로젝트 기본 경로: {base_path}")

    # 생성할 핵심 폴더 목록
    folders_to_create = [
        os.path.join(base_path, 'src'),
        os.path.join(base_path, 'src', 'utils'), # file_helper.py가 위치할 곳
        os.path.join(base_path, 'docs'),
        os.path.join(base_path, 'config'),
        os.path.join(base_path, 'tests'),
        os.path.join(base_path, 'data'), # 수집된 정보 저장용
        os.path.join(base_path, 'logs'), # 로그 파일 저장용
        os.path.join(base_path, 'backup') # 백업 파일 저장용
    ]

    print("\n폴더 구조 생성을 시작합니다...")
    for folder in folders_to_create:
        try:
            # 폴더가 존재하지 않으면 생성
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"  폴더 생성 완료: {folder}")
            else:
                print(f"  폴더 이미 존재: {folder}")
        except OSError as e:
            print(f"  폴더 생성 실패: {folder} - 오류: {e}")
            # 오류 발생 시에도 다른 폴더 생성을 시도하도록 계속 진행

    print("\n프로젝트 폴더 구조 생성이 완료되었습니다.")

# 이 스크립트가 직접 실행될 경우를 위한 예시
if __name__ == "__main__":
    # 서대리의 작업 환경에 맞춰 D:\AI_Project\GIAv2.0 경로를 사용합니다.
    # 실제 실행 시에는 이 부분을 호출하지 않거나, 호출 시 주의해야 합니다.
    # 이 파일은 주로 다른 스크립트에서 import 되어 사용될 것입니다.
    print("이 파일은 주로 모듈로 import 되어 사용됩니다.")
    print("만약 직접 실행하여 폴더 구조를 생성하려면, 아래 주석을 해제하세요.")
    # base_project_path = "D:\\AI_Project\\GIAv2.0"
    # create_project_structure(base_project_path)
