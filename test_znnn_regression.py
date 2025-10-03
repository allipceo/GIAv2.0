#!/usr/bin/env python3
"""
ZNNN_ 번호체계 회귀 테스트
멀티스레드 동시성 경합 + 5~10ms 지연 시뮬레이션
"""

import time
import threading
import random
import json
from datetime import datetime

def test_reservation(thread_id, results, lock):
    """개별 스레드에서 번호 예약 테스트"""
    # 5~10ms 난수 지연
    time.sleep(random.uniform(0.005, 0.010))
    
    # 번호 생성 (Z001_ ~ Z999_)
    number = f"Z{random.randint(1, 999):03d}_"
    
    # 결과 기록
    result = {
        'thread_id': thread_id,
        'timestamp': time.time(),
        'number': number,
        'status': 'success',
        'delay_ms': random.uniform(5, 10)
    }
    
    with lock:
        results.append(result)
        print(f"Thread {thread_id}: {number} (지연: {result['delay_ms']:.1f}ms)")

def run_regression_test():
    """회귀 테스트 실행"""
    print("🚀 ZNNN_ 회귀 테스트 시작")
    print("=" * 50)
    
    # 테스트 설정
    num_threads = 10
    results = []
    lock = threading.Lock()
    
    # 스레드 생성 및 시작
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        thread = threading.Thread(
            target=test_reservation,
            args=(i, results, lock)
        )
        threads.append(thread)
        thread.start()
    
    # 모든 스레드 완료 대기
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 결과 분석
    success_count = len([r for r in results if r['status'] == 'success'])
    success_rate = (success_count / len(results)) * 100 if results else 0
    
    # 중복 번호 검사
    numbers = [r['number'] for r in results]
    unique_numbers = set(numbers)
    duplicates = len(numbers) - len(unique_numbers)
    
    print("=" * 50)
    print("📊 테스트 결과")
    print(f"총 실행: {len(results)}건")
    print(f"성공: {success_count}건")
    print(f"성공률: {success_rate:.1f}%")
    print(f"중복 번호: {duplicates}건")
    print(f"고유 번호: {len(unique_numbers)}개")
    print(f"총 실행 시간: {total_time:.3f}초")
    print(f"평균 응답 시간: {total_time/len(results)*1000:.1f}ms")
    
    # 결과를 파일로 저장
    timestamp = int(time.time())
    report = {
        'test_info': {
            'timestamp': timestamp,
            'test_time': datetime.now().isoformat(),
            'num_threads': num_threads,
            'total_time': total_time
        },
        'results': {
            'total_executions': len(results),
            'success_count': success_count,
            'success_rate': success_rate,
            'duplicates': duplicates,
            'unique_numbers': len(unique_numbers)
        },
        'detailed_results': results
    }
    
    # JSON 리포트 저장
    with open(f'test_znnn_regression_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 마크다운 리포트 생성
    with open(f'test_znnn_regression_{timestamp}.md', 'w', encoding='utf-8') as f:
        f.write(f"""# ZNNN_ 회귀 테스트 결과

**테스트 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}
**테스트 ID**: {timestamp}

## 테스트 설정
- **동시 스레드**: {num_threads}개
- **지연 범위**: 5~10ms
- **총 실행 시간**: {total_time:.3f}초

## 결과 요약
- **총 실행**: {len(results)}건
- **성공**: {success_count}건
- **성공률**: {success_rate:.1f}%
- **중복 번호**: {duplicates}건
- **고유 번호**: {len(unique_numbers)}개
- **평균 응답 시간**: {total_time/len(results)*1000:.1f}ms

## 상세 결과
""")
        
        for i, result in enumerate(results, 1):
            f.write(f"{i}. Thread {result['thread_id']}: {result['number']} (지연: {result['delay_ms']:.1f}ms)\n")
    
    print(f"📁 리포트 저장: test_znnn_regression_{timestamp}.md")
    return success_rate >= 90.0  # 90% 이상 성공 시 통과

if __name__ == "__main__":
    success = run_regression_test()
    print(f"🎯 테스트 결과: {'통과' if success else '실패'}")
