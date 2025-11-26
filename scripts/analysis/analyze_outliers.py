"""데이터 이상치 분석"""
import pandas as pd

print("="*70)
print("🔍 데이터 이상치 분석")
print("="*70)

# ========== 1. 국산차 ==========
print("\n📊 1. 국산차 데이터")
print("-"*50)
df = pd.read_csv('encar_raw_domestic.csv')
print(f"전체: {len(df):,}행")
print(f"Price >= 9999: {len(df[df['Price']>=9999]):,}행 ({len(df[df['Price']>=9999])/len(df)*100:.1f}%)")
print(f"Price == 0: {len(df[df['Price']==0]):,}행")
print(f"Price < 100: {len(df[df['Price']<100]):,}행")

# 9999+ 차량들
print("\n[9999+ 가격 차량 샘플]")
high = df[df['Price'] >= 9999][['Manufacturer','Model','Year','Mileage','Price']].head(15)
print(high.to_string())

# Price 분포
print("\n[Price 분포]")
print(df['Price'].describe())

# ========== 2. 수입차 ==========
print("\n" + "="*70)
print("📊 2. 수입차 데이터")
print("-"*50)
try:
    df_i = pd.read_csv('encar_imported_data.csv')
    print(f"전체: {len(df_i):,}행")
    print(f"Price >= 9999: {len(df_i[df_i['Price']>=9999]):,}행 ({len(df_i[df_i['Price']>=9999])/len(df_i)*100:.1f}%)")
    print(f"Price == 0: {len(df_i[df_i['Price']==0]):,}행")
    print(f"Price < 100: {len(df_i[df_i['Price']<100]):,}행")
    
    # 9999+ 차량들
    print("\n[9999+ 가격 차량 샘플]")
    high_i = df_i[df_i['Price'] >= 9999][['Manufacturer','Model','Year','Mileage','Price']].head(15)
    print(high_i.to_string())
    
    # Price 분포
    print("\n[Price 분포]")
    print(df_i['Price'].describe())
    
    # 비정상 가격 패턴 분석
    print("\n[가격 패턴 분석]")
    for val in [9999, 99999, 11111, 1111]:
        cnt = len(df_i[df_i['Price'] == val])
        if cnt > 0:
            print(f"Price == {val}: {cnt}건")
except Exception as e:
    print(f"수입차 데이터 로드 실패: {e}")

# ========== 3. 결론 ==========
print("\n" + "="*70)
print("💡 이상치 영향 분석")
print("="*70)
print("9999, 11111 등의 가격은 '가격 문의' 또는 데이터 오류일 가능성이 높습니다.")
print("이런 데이터가 학습에 포함되면 모델이 고가 차량을 과대평가할 수 있습니다.")
