"""옵션에 따른 가격 변동 분석"""
import pandas as pd
import numpy as np
import joblib

print("="*70)
print("🔧 옵션에 따른 가격 변동 분석")
print("="*70)

# 데이터 로드
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df['YearOnly'] = (df['Year'] // 100).astype(int)

# 패턴 이상치 제거
patterns = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]
df = df[~df['Price'].isin(patterns)]
df = df[df['Price'] > 100]

print(f"\n데이터: {len(df):,}행")

# 1. 모델/인코더 로드
model = joblib.load('models/domestic_v2.pkl')
feature_cols = joblib.load('models/domestic_v2_features.pkl')

print("\n" + "="*70)
print("1️⃣ 옵션 관련 피처 중요도")
print("-"*70)

# Feature Importance
importance = model.feature_importances_
feat_imp = pd.DataFrame({
    'feature': feature_cols,
    'importance': importance
}).sort_values('importance', ascending=False)

option_features = ['option_count', 'option_rate', 'option_premium', 
                   'has_sunroof', 'has_led_lamp', 'has_leather_seat', 
                   'has_smart_key', 'enc_x_option']

print("\n전체 피처 중요도 (상위 15개):")
for i, row in feat_imp.head(15).iterrows():
    marker = "⭐" if row['feature'] in option_features else "  "
    print(f"{marker} {row['feature']}: {row['importance']:.4f} ({row['importance']*100:.1f}%)")

print("\n옵션 관련 피처만:")
option_imp = feat_imp[feat_imp['feature'].isin(option_features)]
total_option_imp = option_imp['importance'].sum()
for _, row in option_imp.iterrows():
    print(f"  {row['feature']}: {row['importance']:.4f} ({row['importance']*100:.1f}%)")
print(f"\n옵션 피처 총 중요도: {total_option_imp:.4f} ({total_option_imp*100:.1f}%)")

# 2. 실제 옵션별 가격 차이 분석
print("\n" + "="*70)
print("2️⃣ 실제 데이터에서 옵션별 가격 차이")
print("-"*70)

# 옵션 컬럼 확인
option_cols = [c for c in df.columns if 'option' in c.lower() or 'has_' in c.lower()]
print(f"옵션 관련 컬럼: {option_cols}")

# 특정 모델로 옵션 영향 분석 (더 뉴 그랜저 IG 2022년)
granger = df[(df['Model']=='더 뉴 그랜저 IG') & (df['YearOnly']==2022)]
print(f"\n더 뉴 그랜저 IG 2022년 (n={len(granger)})")

if 'has_sunroof' in granger.columns:
    sunroof_yes = granger[granger['has_sunroof']==1]['Price'].median()
    sunroof_no = granger[granger['has_sunroof']==0]['Price'].median()
    print(f"  선루프 O: {sunroof_yes:,.0f}만원 / 선루프 X: {sunroof_no:,.0f}만원 (차이: {sunroof_yes-sunroof_no:+,.0f}만원)")

if 'has_leather_seat' in granger.columns:
    leather_yes = granger[granger['has_leather_seat']==1]['Price'].median()
    leather_no = granger[granger['has_leather_seat']==0]['Price'].median()
    print(f"  가죽시트 O: {leather_yes:,.0f}만원 / 가죽시트 X: {leather_no:,.0f}만원 (차이: {leather_yes-leather_no:+,.0f}만원)")

if 'has_navigation' in granger.columns:
    nav_yes = granger[granger['has_navigation']==1]['Price'].median()
    nav_no = granger[granger['has_navigation']==0]['Price'].median()
    print(f"  네비 O: {nav_yes:,.0f}만원 / 네비 X: {nav_no:,.0f}만원 (차이: {nav_yes-nav_no:+,.0f}만원)")

# 3. 옵션 개수에 따른 가격
print("\n" + "="*70)
print("3️⃣ 옵션 개수에 따른 가격 (그랜저 IG 2022년)")
print("-"*70)

if 'option_count' in granger.columns:
    option_price = granger.groupby('option_count')['Price'].agg(['median', 'count'])
    option_price = option_price[option_price['count'] >= 5]
    for opt_cnt, row in option_price.iterrows():
        print(f"  옵션 {opt_cnt}개: 중앙값 {row['median']:,.0f}만원 (n={row['count']:.0f})")

# 4. API 예측에서 옵션 영향 테스트
print("\n" + "="*70)
print("4️⃣ API 예측에서 옵션 영향 시뮬레이션")
print("-"*70)

import requests

base_params = {
    'brand': '현대',
    'model': '더 뉴 그랜저 IG',
    'year': 2022,
    'mileage': 30000,
    'fuel': '가솔린'
}

# 현재 API는 옵션 파라미터를 받지 않음 - 기본값 사용
resp = requests.post('http://localhost:8000/api/predict', json=base_params)
pred = resp.json()['predicted_price']
print(f"현재 API 예측 (기본 옵션): {pred:,.0f}만원")

print("\n💡 현재 모델의 한계:")
print("  - API가 옵션 정보를 입력받지 않음")
print("  - 모든 예측에서 기본 옵션값(평균) 사용")
print("  - 옵션이 풀/노옵션인 경우 오차 발생")

# 5. 옵션 영향 추정
print("\n" + "="*70)
print("5️⃣ 옵션에 따른 예상 가격 범위")
print("-"*70)

encoders = joblib.load('models/domestic_v2_encoders.pkl')
mym_enc = encoders.get('Model_Year_Mileage_enc', {})

# 그랜저 2022 B그룹 인코딩 값
mym_val = mym_enc.get('더 뉴 그랜저 IG_2022_B', 8.0)
base_price = np.expm1(mym_val)

print(f"그랜저 IG 2022년 3만km 기준가: {base_price:,.0f}만원")
print(f"\n예상 옵션 영향:")
print(f"  풀옵션 (프리미엄): +{base_price*0.08:,.0f}만원 (약 +8%)")
print(f"  일반옵션 (기본):   ±0만원")
print(f"  노옵션 (저가형):   -{base_price*0.05:,.0f}만원 (약 -5%)")
print(f"\n예상 가격 범위: {base_price*0.95:,.0f} ~ {base_price*1.08:,.0f}만원")
