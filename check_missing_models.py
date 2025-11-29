import pandas as pd
import os

df = pd.read_csv('data/processed_encar_combined.csv', encoding='utf-8')
folder = r'차량 이미지\차량 이미지'
folder_images = set(f.replace('.png', '') for f in os.listdir(folder) if f.endswith('.png'))

# 현재 CarImageMapper의 부분 매칭 키워드 (국산차만 있음)
partial_keys = [
    '그랜저', '쏘나타', '아반떼', '투싼', '싼타페', '팰리세이드', '스타리아', '스타렉스', '코나',
    '아이오닉', '캐스퍼', '베뉴', '베리타스', '슈퍼살롱', '다마스', '라보', '포텐샤',
    '쏘렌토', '카니발', '모닝', '레이', '니로', '셀토스', '스팅어', '스포티지',
    '스토닉', '쏘울', '포르테', '카렌스', '프라이드', '타스만', '엔터프라이즈',
    'K3', 'K5', 'K7', 'K8', 'K9', 'EV3', 'EV4', 'EV5', 'EV6', 'EV9', 'PV5',
    'G70', 'G80', 'G90', 'G2X', 'GV60', 'GV70', 'GV80',
    'SM3', 'SM5', 'SM6', 'SM7', 'QM3', 'QM5', 'QM6', 'XM3',
    '클리오', '조에', '캡처', '마스터', '아르카나', '콜레오스',
    '스파크', '크루즈', '말리부', '임팔라', '트랙스', '이쿼녹스',
    '트래버스', '볼트', '캡티바', '올란도', '토스카', '콜로라도', '타호',
    '라세티', '젠트라', '알페온', '마티즈', '아베오', '윈스톰', '카마로',
    '티볼리', '토레스', '코란도', '렉스턴', '모하비', '액티언',
    '무쏘', '체어맨', '로디우스', '이스타나',
    '로체', '티코', '프레지오',
]

def is_covered(model_name):
    """현재 이미지+부분매칭으로 커버되는지"""
    if model_name in folder_images:
        return True
    for key in partial_keys:
        if key in model_name:
            return True
    return False

# 수입차 브랜드 목록 (이미지가 필요한)
import_brands = ['BMW', '벤츠', '아우디', '폭스바겐', '포르쉐', '렉서스', '도요타', '혼다',
                  '테슬라', '볼보', '미니', '재규어', '랜드로버', '페라리', '람보르기니',
                  '마세라티', '벤틀리', '롤스로이스', '애스턴마틴', '맥라렌', '포드', '링컨',
                  '캐딜락', '지프', '닛산', '인피니티', '푸조', '시트로엥/DS', '피아트', '폴스타']

# 각 브랜드별로 커버 안되는 모델과 데이터 건수
print("=" * 70)
print("수입차 브랜드별 이미지 필요 모델 (데이터 건수 순)")
print("=" * 70)

for brand in import_brands:
    brand_df = df[df['brand'] == brand]
    if len(brand_df) == 0:
        continue

    # 모델별 집계
    model_counts = brand_df.groupby('model_name').size().sort_values(ascending=False)

    # 커버 안되는 모델들
    uncovered = []
    covered_count = 0
    for model, count in model_counts.items():
        if not is_covered(model):
            uncovered.append((model, count))
        else:
            covered_count += count

    if uncovered:
        total = len(brand_df)
        uncovered_total = sum(c for _, c in uncovered)
        print(f"\n[{brand}] 총 {total}건 중 {uncovered_total}건 미커버 ({uncovered_total/total*100:.1f}%)")
        print("-" * 50)

        # 대표 모델 추출 (공통 키워드로 그룹핑)
        model_groups = {}
        for model, count in uncovered:
            # 대표 키워드 추출 (시리즈명)
            key = None
            for kw in ['시리즈', '클래스', '-클래스', '클래스 ', 'A', 'B', 'C', 'E', 'S', 'G', 'CLA', 'CLS', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'AMG', 'EQ']:
                pass  # 나중에
            model_groups[model] = count

        # 상위 10개만 출력
        for model, count in uncovered[:10]:
            print(f"  {model}: {count}건")
        if len(uncovered) > 10:
            print(f"  ... 외 {len(uncovered)-10}개 모델")

