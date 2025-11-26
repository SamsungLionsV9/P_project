"""
입력 데이터 검증
"""

from typing import List, Tuple


# 지원하는 브랜드 목록
SUPPORTED_BRANDS = [
    "현대", "기아", "제네시스", 
    "벤츠", "BMW", "아우디", "폭스바겐", "볼보", "푸조", "시트로엥", "르노", "미니",
    "렉서스", "토요타", "혼다", "닛산", "인피니티", "마쓰다",
    "쉐보레", "포드", "지프", "링컨", "캐딜락", "테슬라",
    "포르쉐", "재규어", "랜드로버", "벤틀리", "롤스로이스", "애스턴마틴", "람보르기니", "페라리"
]

# 지원하는 연료 타입
SUPPORTED_FUEL_TYPES = [
    "가솔린", "디젤", "LPG", "하이브리드", "전기", 
    "가솔린+LPG", "가솔린+전기", "수소"
]

# 브랜드별 인기 모델 (예시)
POPULAR_MODELS = {
    "현대": ["그랜저", "쏘나타", "아반떼", "투싼", "팰리세이드", "산타페", "코나", "벨로스터"],
    "기아": ["K5", "K7", "K8", "K9", "쏘렌토", "스포티지", "셀토스", "니로", "카니발", "모닝"],
    "제네시스": ["G70", "G80", "G90", "GV70", "GV80"],
    "벤츠": ["E클래스", "C클래스", "S클래스", "GLC", "GLE", "GLA", "A클래스"],
    "BMW": ["3시리즈", "5시리즈", "7시리즈", "X3", "X5", "X7"],
    "아우디": ["A4", "A6", "A8", "Q5", "Q7", "Q3"],
    "테슬라": ["모델 3", "모델 S", "모델 X", "모델 Y"],
}


def validate_brand(brand: str) -> Tuple[bool, str]:
    """
    브랜드 검증
    
    Args:
        brand: 브랜드명
        
    Returns:
        (유효성, 메시지)
    """
    if not brand:
        return False, "브랜드를 입력해주세요"
    
    # 정확한 매칭은 아니지만, 유사한 브랜드는 허용
    brand_lower = brand.lower()
    for supported in SUPPORTED_BRANDS:
        if supported.lower() in brand_lower or brand_lower in supported.lower():
            return True, ""
    
    return True, f"경고: '{brand}'는 자주 사용되지 않는 브랜드입니다"


def validate_model(model: str, brand: str = None) -> Tuple[bool, str]:
    """
    모델명 검증
    
    Args:
        model: 모델명
        brand: 브랜드명 (선택)
        
    Returns:
        (유효성, 메시지)
    """
    if not model:
        return False, "모델명을 입력해주세요"
    
    if len(model) < 2:
        return False, "모델명이 너무 짧습니다"
    
    # 브랜드가 주어진 경우, 해당 브랜드의 인기 모델인지 확인
    if brand and brand in POPULAR_MODELS:
        popular = POPULAR_MODELS[brand]
        for pop_model in popular:
            if pop_model.lower() in model.lower() or model.lower() in pop_model.lower():
                return True, ""
        return True, f"경고: '{model}'는 {brand}의 자주 검색되지 않는 모델입니다"
    
    return True, ""


def validate_year(year: int) -> Tuple[bool, str]:
    """
    연식 검증
    
    Args:
        year: 연식
        
    Returns:
        (유효성, 메시지)
    """
    if year < 1990:
        return False, "연식은 1990년 이상이어야 합니다"
    
    if year > 2025:
        return False, "연식은 2025년 이하여야 합니다"
    
    if year < 2000:
        return True, f"경고: {year}년식은 매우 오래된 차량입니다"
    
    return True, ""


def validate_mileage(mileage: int, year: int = None) -> Tuple[bool, str]:
    """
    주행거리 검증
    
    Args:
        mileage: 주행거리 (km)
        year: 연식 (선택)
        
    Returns:
        (유효성, 메시지)
    """
    if mileage < 0:
        return False, "주행거리는 0 이상이어야 합니다"
    
    if mileage > 500000:
        return False, "주행거리가 너무 많습니다 (50만km 이상)"
    
    # 연식이 주어진 경우, 연평균 주행거리 계산
    if year:
        age = 2025 - year
        if age > 0:
            annual_mileage = mileage / age
            if annual_mileage > 30000:
                return True, f"경고: 연평균 주행거리가 {annual_mileage:,.0f}km로 많습니다"
            elif annual_mileage < 5000:
                return True, f"경고: 연평균 주행거리가 {annual_mileage:,.0f}km로 적습니다 (주행거리 조작 의심)"
    
    return True, ""


def validate_fuel(fuel: str) -> Tuple[bool, str]:
    """
    연료 타입 검증
    
    Args:
        fuel: 연료 타입
        
    Returns:
        (유효성, 메시지)
    """
    if not fuel:
        return False, "연료 타입을 입력해주세요"
    
    # 유사한 연료 타입 허용
    fuel_lower = fuel.lower()
    for supported in SUPPORTED_FUEL_TYPES:
        if supported.lower() in fuel_lower or fuel_lower in supported.lower():
            return True, ""
    
    return True, f"경고: '{fuel}'는 자주 사용되지 않는 연료 타입입니다"


def validate_vehicle_data(brand: str, model: str, year: int, mileage: int, fuel: str) -> Tuple[bool, List[str]]:
    """
    차량 데이터 종합 검증
    
    Args:
        brand: 브랜드
        model: 모델명
        year: 연식
        mileage: 주행거리
        fuel: 연료
        
    Returns:
        (유효성, 경고/에러 메시지 리스트)
    """
    messages = []
    is_valid = True
    
    # 브랜드 검증
    valid, msg = validate_brand(brand)
    if not valid:
        is_valid = False
        messages.append(f"❌ {msg}")
    elif msg:
        messages.append(f"⚠️ {msg}")
    
    # 모델 검증
    valid, msg = validate_model(model, brand)
    if not valid:
        is_valid = False
        messages.append(f"❌ {msg}")
    elif msg:
        messages.append(f"⚠️ {msg}")
    
    # 연식 검증
    valid, msg = validate_year(year)
    if not valid:
        is_valid = False
        messages.append(f"❌ {msg}")
    elif msg:
        messages.append(f"⚠️ {msg}")
    
    # 주행거리 검증
    valid, msg = validate_mileage(mileage, year)
    if not valid:
        is_valid = False
        messages.append(f"❌ {msg}")
    elif msg:
        messages.append(f"⚠️ {msg}")
    
    # 연료 검증
    valid, msg = validate_fuel(fuel)
    if not valid:
        is_valid = False
        messages.append(f"❌ {msg}")
    elif msg:
        messages.append(f"⚠️ {msg}")
    
    return is_valid, messages


def get_supported_brands() -> List[str]:
    """지원하는 브랜드 목록 반환"""
    return SUPPORTED_BRANDS


def get_supported_fuel_types() -> List[str]:
    """지원하는 연료 타입 목록 반환"""
    return SUPPORTED_FUEL_TYPES


def get_models_by_brand(brand: str) -> List[str]:
    """브랜드별 모델 목록 반환"""
    return POPULAR_MODELS.get(brand, [])

