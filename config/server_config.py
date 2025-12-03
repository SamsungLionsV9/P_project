"""
서버 설정 파일
run_server.py의 하드코딩된 값들을 중앙 관리

[리팩토링]
- 환경 변수 또는 .env 파일에서 민감 정보 로드
- 브랜드/모델 데이터는 별도 JSON 또는 DB에서 로드
"""

import os
from typing import Dict, List

# ========== 환경 설정 ==========
SPRING_BOOT_URL = os.getenv("SPRING_BOOT_URL", "http://localhost:8080")
ML_SERVICE_PORT = int(os.getenv("ML_SERVICE_PORT", 8000))

# ========== 관리자 계정 (환경변수로 이동 권장) ==========
# TODO: 실제 운영 시 환경 변수 또는 DB에서 로드
ADMIN_ACCOUNTS = {
    "admin@carsentix.com": {
        "password": os.getenv("ADMIN_PASSWORD", "admin1234!"),
        "id": 1,
        "username": "관리자",
        "role": "ADMIN"
    },
    "admin@car-sentix.com": {
        "password": os.getenv("ADMIN_PASSWORD", "admin1234!"),
        "id": 1,
        "username": "관리자",
        "role": "ADMIN"
    },
}

# ========== 기본 사용자 목록 ==========
DEFAULT_USERS = [
    {
        "id": 1,
        "email": "admin@car-sentix.com",
        "username": "관리자",
        "phoneNumber": "010-1234-5678",
        "role": "ADMIN",
        "provider": "LOCAL",
        "isActive": True
    },
    {
        "id": 3,
        "email": "guest",
        "username": "게스트",
        "phoneNumber": "-",
        "role": "GUEST",
        "provider": "LOCAL",
        "isActive": True
    },
]

# ========== 차량 브랜드/모델 데이터 ==========
# TODO: data/brands.json으로 분리 권장

DOMESTIC_BRANDS = ['현대', '기아', '제네시스', '쉐보레', 'KG모빌리티', '르노코리아']
IMPORTED_BRANDS = ['BMW', '벤츠', '아우디', '폭스바겐', '볼보', '렉서스', '토요타', '혼다', 
                   '포르쉐', '랜드로버', '재규어', '미니', '푸조', '시트로엥', '포드', '지프', '테슬라']

BRAND_MODELS: Dict[str, List[str]] = {
    # 국산차
    '현대': ['그랜저', '쏘나타', '아반떼', '투싼', '싼타페', '팰리세이드', '코나', '베뉴', '아이오닉5', '아이오닉6', 'G70', 'G80', 'G90', 'GV60', 'GV70', 'GV80'],
    '기아': ['K3', 'K5', 'K8', 'K9', '스포티지', '쏘렌토', '카니발', '셀토스', '니로', 'EV6', 'EV9'],
    '제네시스': ['G70', 'G80', 'G90', 'GV60', 'GV70', 'GV80'],
    '쉐보레': ['말리부', '트랙스', '트레일블레이저', '이쿼녹스', '타호', '콜로라도', '볼트EV', '볼트EUV'],
    'KG모빌리티': ['토레스', '렉스턴', '코란도', '티볼리', '액티언'],
    '르노코리아': ['SM6', 'XM3', 'QM6', '아르카나', '조에'],
    
    # 수입차
    'BMW': ['1시리즈', '2시리즈', '3시리즈', '4시리즈', '5시리즈', '7시리즈', 'X1', 'X3', 'X5', 'X6', 'X7', 'iX', 'i4', 'i7'],
    '벤츠': ['A-클래스', 'C-클래스', 'E-클래스', 'S-클래스', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'EQE', 'EQS'],
    '아우디': ['A3', 'A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8', 'e-tron', 'e-tron GT'],
    '폭스바겐': ['골프', '파사트', '티구안', '투아렉', 'ID.4'],
    '볼보': ['S60', 'S90', 'XC40', 'XC60', 'XC90', 'C40', 'EX30', 'EX90'],
    '렉서스': ['ES', 'IS', 'LS', 'NX', 'RX', 'LX', 'UX'],
    '토요타': ['캠리', 'RAV4', '프리우스', '하이랜더', '시에나'],
    '혼다': ['어코드', 'CR-V', 'HR-V', '시빅', '파일럿'],
    '포르쉐': ['911', '카이엔', '마칸', '파나메라', '타이칸'],
    '랜드로버': ['레인지로버', '레인지로버 스포츠', '디펜더', '디스커버리', '이보크'],
    '재규어': ['XE', 'XF', 'F-PACE', 'I-PACE', 'E-PACE'],
    '미니': ['쿠퍼', '클럽맨', '컨트리맨'],
    '테슬라': ['모델3', '모델Y', '모델S', '모델X', '사이버트럭'],
}

def get_all_brands() -> List[str]:
    """모든 브랜드 목록 반환"""
    return DOMESTIC_BRANDS + IMPORTED_BRANDS

def get_models_by_brand(brand: str) -> List[str]:
    """브랜드별 모델 목록 반환"""
    return BRAND_MODELS.get(brand, [])

def is_domestic_brand(brand: str) -> bool:
    """국산 브랜드 여부 확인"""
    return brand in DOMESTIC_BRANDS
