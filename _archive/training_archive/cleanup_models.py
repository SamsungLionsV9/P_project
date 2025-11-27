"""
모델 파일 정리 스크립트
======================
Production에 필요한 V11 파일만 남기고 나머지는 archive로 이동
"""
import os
import shutil

MODEL_DIR = 'models'
ARCHIVE_DIR = 'models/archive'

# Production 파일 (유지)
KEEP_FILES = {
    'domestic_v11.pkl',
    'domestic_v11_encoders.pkl', 
    'domestic_v11_features.pkl',
    'imported_v11.pkl',
    'imported_v11_encoders.pkl',
    'imported_v11_features.pkl',
}

def cleanup():
    # Archive 폴더 생성
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    moved = []
    kept = []
    
    for f in os.listdir(MODEL_DIR):
        if f == 'archive':
            continue
        
        src = os.path.join(MODEL_DIR, f)
        if os.path.isfile(src):
            if f in KEEP_FILES:
                kept.append(f)
            else:
                dst = os.path.join(ARCHIVE_DIR, f)
                shutil.move(src, dst)
                moved.append(f)
    
    print("="*60)
    print("📁 모델 파일 정리 완료")
    print("="*60)
    
    print(f"\n✅ Production 유지 ({len(kept)}개):")
    for f in sorted(kept):
        print(f"   {f}")
    
    print(f"\n📦 Archive 이동 ({len(moved)}개):")
    for f in sorted(moved)[:10]:
        print(f"   {f}")
    if len(moved) > 10:
        print(f"   ... 외 {len(moved)-10}개")
    
    print(f"\n📍 Archive 위치: {os.path.abspath(ARCHIVE_DIR)}")

if __name__ == "__main__":
    confirm = input("모델 파일을 정리하시겠습니까? (y/n): ")
    if confirm.lower() == 'y':
        cleanup()
    else:
        print("취소됨")
