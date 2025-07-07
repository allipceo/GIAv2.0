# D:\AI_Project\GIAv2.0\src\utils\file_helper.py

import os
import shutil
import datetime

def get_file_size_kb(file_path):
    """
    파일의 크기를 킬로바이트(KB) 단위로 반환합니다.

    Args:
        file_path (str): 파일의 전체 경로.

    Returns:
        float: 파일 크기 (KB) 또는 파일이 없으면 -1.
    """
    if not os.path.exists(file_path):
        print(f"경고: 파일이 존재하지 않습니다 - {file_path}")
        return -1
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / 1024.0 # 바이트를 킬로바이트로 변환
    except Exception as e:
        print(f"파일 크기를 가져오는 중 오류 발생: {file_path} - {e}")
        return -1

def create_file_backup(source_file_path, backup_dir="D:\\AI_Project\\GIAv2.0\\backup"):
    """
    지정된 파일을 백업 디렉토리에 복사합니다.
    백업 파일명은 '원본파일명_YYYYMMDD_HHMMSS.확장자' 형식으로 생성됩니다.

    Args:
        source_file_path (str): 백업할 원본 파일의 전체 경로.
        backup_dir (str): 백업 파일을 저장할 디렉토리 경로. 기본값은 프로젝트 내 backup 폴더.

    Returns:
        str: 생성된 백업 파일의 전체 경로 또는 백업 실패 시 None.
    """
    if not os.path.exists(source_file_path):
        print(f"오류: 백업할 원본 파일이 존재하지 않습니다 - {source_file_path}")
        return None

    # 백업 디렉토리가 없으면 생성
    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir)
            print(f"백업 디렉토리 생성: {backup_dir}")
        except OSError as e:
            print(f"오류: 백업 디렉토리 생성 실패 - {backup_dir} - {e}")
            return None

    # 파일명과 확장자 분리
    base_name = os.path.basename(source_file_path)
    file_name_without_ext, file_extension = os.path.splitext(base_name)

    # 현재 시간으로 백업 파일명 생성
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file_name = f"{file_name_without_ext}_{timestamp}{file_extension}"
    destination_path = os.path.join(backup_dir, backup_file_name)

    try:
        shutil.copy2(source_file_path, destination_path) # 메타데이터도 함께 복사
        print(f"파일 백업 성공: {source_file_path} -> {destination_path}")
        return destination_path
    except Exception as e:
        print(f"파일 백업 실패: {source_file_path} - 오류: {e}")
        return None

# 이 스크립트가 직접 실행될 경우를 위한 예시
if __name__ == "__main__":
    # 테스트를 위한 임시 파일 생성
    test_file_path = "D:\\AI_Project\\GIAv2.0\\temp_test_file.txt"
    with open(test_file_path, "w") as f:
        f.write("이것은 테스트 파일입니다.\n")
        f.write("파일 크기 및 백업 기능을 테스트합니다.")

    print(f"테스트 파일 생성: {test_file_path}")

    # 파일 크기 확인
    size_kb = get_file_size_kb(test_file_path)
    if size_kb != -1:
        print(f"테스트 파일 크기: {size_kb:.2f} KB")

    # 파일 백업
    backup_path = create_file_backup(test_file_path)
    if backup_path:
        print(f"생성된 백업 파일: {backup_path}")

    # 테스트 파일 삭제 (선택 사항)
    # os.remove(test_file_path)
    # print(f"테스트 파일 삭제: {test_file_path}")
