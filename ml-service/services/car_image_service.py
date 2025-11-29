"""
Car Image Service - 차량 이미지 매핑
====================================
브랜드/모델별 대표 이미지 URL 관리
- 실제 차량 이미지 CDN URL 매핑
- 모델명 유사도 기반 이미지 검색
"""

from typing import Dict, Optional

class CarImageService:
    """차량 이미지 매핑 서비스"""
    
    # 브랜드별 로고 이미지 (Wikimedia Commons CDN)
    BRAND_LOGOS = {
        "현대": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Hyundai_Motor_Company_logo.svg/200px-Hyundai_Motor_Company_logo.svg.png",
        "기아": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Kia-logo.svg/200px-Kia-logo.svg.png",
        "제네시스": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Genesis_Logo.svg/200px-Genesis_Logo.svg.png",
        "쉐보레": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Chevrolet-logo-2011-.svg/200px-Chevrolet-logo-2011-.svg.png",
        "르노삼성": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Renault_Samsung_Motors.svg/200px-Renault_Samsung_Motors.svg.png",
        "르노코리아": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Renault_Samsung_Motors.svg/200px-Renault_Samsung_Motors.svg.png",
        "쌍용": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/SsangYong_logo.svg/200px-SsangYong_logo.svg.png",
        "KG모빌리티": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/SsangYong_logo.svg/200px-SsangYong_logo.svg.png",
        "BMW": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/200px-BMW.svg.png",
        "벤츠": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/200px-Mercedes-Logo.svg.png",
        "메르세데스-벤츠": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/200px-Mercedes-Logo.svg.png",
        "아우디": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Audi-Logo_2016.svg/200px-Audi-Logo_2016.svg.png",
        "폭스바겐": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Volkswagen_logo_2019.svg/200px-Volkswagen_logo_2019.svg.png",
        "볼보": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Volvo_logo.svg/200px-Volvo_logo.svg.png",
        "렉서스": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Lexus_division_emblem.svg/200px-Lexus_division_emblem.svg.png",
        "토요타": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Toyota.svg/200px-Toyota.svg.png",
        "혼다": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Honda.svg/200px-Honda.svg.png",
        "포르쉐": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Porsche_logo.svg/200px-Porsche_logo.svg.png",
        "재규어": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Jaguar_2012_logo.svg/200px-Jaguar_2012_logo.svg.png",
        "랜드로버": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Land_Rover_logo.svg/200px-Land_Rover_logo.svg.png",
        "미니": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Mini_logo.svg/200px-Mini_logo.svg.png",
        "테슬라": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Tesla_Motors.svg/200px-Tesla_Motors.svg.png",
        "지프": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Jeep_logo.svg/200px-Jeep_logo.svg.png",
        "포드": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Ford_Motor_Company_Logo.svg/200px-Ford_Motor_Company_Logo.svg.png",
    }
    
    # 인기 모델별 대표 이미지 (Unsplash API 활용 가능, 현재는 placeholder)
    MODEL_IMAGES = {
        # 현대
        "그랜저": "https://www.hyundai.com/contents/vr360/GN07/exterior/P2F/001.png",
        "쏘나타": "https://www.hyundai.com/contents/vr360/DN08/exterior/NB9/001.png",
        "아반떼": "https://www.hyundai.com/contents/vr360/CN01/exterior/T2X/001.png",
        "투싼": "https://www.hyundai.com/contents/vr360/NX06/exterior/SSS/001.png",
        "싼타페": "https://www.hyundai.com/contents/vr360/MX05/exterior/TCN/001.png",
        "팰리세이드": "https://www.hyundai.com/contents/vr360/LX03/exterior/R2T/001.png",
        "코나": "https://www.hyundai.com/contents/vr360/SX2E/exterior/P7V/001.png",
        "아이오닉5": "https://www.hyundai.com/contents/vr360/NE01/exterior/SAW/001.png",
        "아이오닉6": "https://www.hyundai.com/contents/vr360/CE02/exterior/P2F/001.png",
        "스타리아": "https://www.hyundai.com/contents/vr360/US04/exterior/P7V/001.png",
        "캐스퍼": "https://www.hyundai.com/contents/vr360/AX01/exterior/T4Y/001.png",
        "더 뉴 투싼": "https://www.hyundai.com/contents/vr360/NX06/exterior/SSS/001.png",
        "더 뉴 그랜저": "https://www.hyundai.com/contents/vr360/GN07/exterior/P2F/001.png",
        
        # 기아
        "K5": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/k5-2024/exterior/k5-ext-front.png",
        "K8": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/k8-2024/exterior/k8-ext-front.png",
        "쏘렌토": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/sorento-2024/exterior/sorento-ext-front.png",
        "스포티지": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/sportage-2024/exterior/sportage-ext-front.png",
        "카니발": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/carnival-2024/exterior/carnival-ext-front.png",
        "모닝": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/morning-2024/exterior/morning-ext-front.png",
        "레이": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/ray-2024/exterior/ray-ext-front.png",
        "셀토스": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/seltos-2024/exterior/seltos-ext-front.png",
        "니로": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/niro-2024/exterior/niro-ext-front.png",
        "EV6": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/ev6-2024/exterior/ev6-ext-front.png",
        "EV9": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/ev9-2024/exterior/ev9-ext-front.png",
        
        # 제네시스
        "G70": "https://www.genesis.com/content/dam/genesis-p2/kr/assets/models/g70/exterior/genesis-g70-exterior.png",
        "G80": "https://www.genesis.com/content/dam/genesis-p2/kr/assets/models/g80/exterior/genesis-g80-exterior.png",
        "G90": "https://www.genesis.com/content/dam/genesis-p2/kr/assets/models/g90/exterior/genesis-g90-exterior.png",
        "GV60": "https://www.genesis.com/content/dam/genesis-p2/kr/assets/models/gv60/exterior/genesis-gv60-exterior.png",
        "GV70": "https://www.genesis.com/content/dam/genesis-p2/kr/assets/models/gv70/exterior/genesis-gv70-exterior.png",
        "GV80": "https://www.genesis.com/content/dam/genesis-p2/kr/assets/models/gv80/exterior/genesis-gv80-exterior.png",
    }
    
    # 기본 이미지 (모델을 찾지 못한 경우)
    DEFAULT_CAR_IMAGE = "https://cdn-icons-png.flaticon.com/512/3774/3774278.png"
    DEFAULT_BRAND_LOGO = "https://cdn-icons-png.flaticon.com/512/3774/3774278.png"
    
    @classmethod
    def get_model_image(cls, brand: str, model: str) -> str:
        """모델별 이미지 URL 반환"""
        # 정확한 모델명 매치
        if model in cls.MODEL_IMAGES:
            return cls.MODEL_IMAGES[model]
        
        # 부분 매칭 시도
        for key, url in cls.MODEL_IMAGES.items():
            if key in model or model in key:
                return url
        
        # 브랜드 로고 반환
        return cls.get_brand_logo(brand)
    
    @classmethod
    def get_brand_logo(cls, brand: str) -> str:
        """브랜드 로고 URL 반환"""
        return cls.BRAND_LOGOS.get(brand, cls.DEFAULT_BRAND_LOGO)
    
    @classmethod
    def get_image_with_fallback(cls, brand: str, model: str, detail_url: str = None) -> Dict:
        """이미지 URL 및 폴백 정보 반환"""
        model_image = cls.get_model_image(brand, model)
        brand_logo = cls.get_brand_logo(brand)
        
        return {
            "model_image": model_image,
            "brand_logo": brand_logo,
            "has_real_image": model in cls.MODEL_IMAGES,
            "fallback_type": "model" if model in cls.MODEL_IMAGES else "brand"
        }
    
    @classmethod
    def add_model_image(cls, model: str, image_url: str):
        """새 모델 이미지 추가 (런타임)"""
        cls.MODEL_IMAGES[model] = image_url


# 싱글톤 인스턴스
car_image_service = CarImageService()

