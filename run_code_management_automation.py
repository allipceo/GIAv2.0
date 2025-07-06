import subprocess

def run_scanner():
    subprocess.run(['python', 'create_intelligent_code_scanner.py'])

def run_manual():
    subprocess.run(['python', 'setup_advanced_code_repository.py'])

def main():
    print('[INFO] 코드 관리 자동화 전체 실행 시작')
    run_scanner()
    run_manual()
    print('[SUCCESS] 코드 관리 자동화 전체 실행 완료')

if __name__ == '__main__':
    main() 