"""
전체 모델 일괄 학습 스크립트
1. 제네시스 모델
2. 일반 국산차 모델 (제네시스 제외)
3. 수입차 모델 (나중에)
"""
import subprocess
import sys
import time
from datetime import datetime

def run_training(script_name, model_name):
    """학습 스크립트 실행"""
    print("\n" + "="*80)
    print(f"🚀 {model_name} 학습 시작...")
    print("="*80)
    print(f"⏰ 시작 시각: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        
        elapsed = time.time() - start_time
        print()
        print("="*80)
        print(f"✅ {model_name} 학습 완료!")
        print(f"⏱️ 소요 시간: {elapsed/60:.1f}분")
        print("="*80)
        
        return True
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print()
        print("="*80)
        print(f"❌ {model_name} 학습 실패!")
        print(f"⏱️ 소요 시간: {elapsed/60:.1f}분")
        print(f"오류: {e}")
        print("="*80)
        
        return False

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🎯 중고차 가격 예측 모델 일괄 학습")
    print("="*80)
    print(f"⏰ 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    total_start = time.time()
    results = {}
    
    # 1. 제네시스 모델 (최종 버전)
    results['제네시스'] = run_training('train_genesis_ultimate.py', '제네시스 최종 모델')
    time.sleep(2)
    
    # 2. 일반 국산차 모델 (최종 버전)
    results['국산차'] = run_training('train_domestic_ultimate.py', '국산차 최종 모델')
    time.sleep(2)
    
    # 3. 수입차 모델 (최종 버전)
    results['수입차'] = run_training('train_imported_ultimate.py', '수입차 최종 모델')
    
    # 최종 결과
    total_elapsed = time.time() - total_start
    
    print("\n\n")
    print("="*80)
    print("📊 전체 학습 결과")
    print("="*80)
    print()
    
    for model_name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"   {model_name:15s}: {status}")
    
    print()
    print(f"⏱️ 총 소요 시간: {total_elapsed/60:.1f}분")
    print(f"⏰ 완료 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 성공한 모델 목록
    success_models = [name for name, success in results.items() if success]
    if success_models:
        print()
        print("✅ 학습 완료된 모델:")
        for model_name in success_models:
            print(f"   - {model_name}")
    
    # 실패한 모델 목록
    failed_models = [name for name, success in results.items() if not success]
    if failed_models:
        print()
        print("❌ 학습 실패한 모델:")
        for model_name in failed_models:
            print(f"   - {model_name}")
    
    print("="*80)

if __name__ == "__main__":
    main()
