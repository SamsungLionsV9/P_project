"""
모델명 필터링 유틸리티
=====================
- 정확한 모델 계열 매칭 (E-클래스 ↔ E-클래스, GLE-클래스 ↔ GLE-클래스)
- 테슬라 모델 구분 (모델 3 ↔ 모델 3, 모델 Y ↔ 모델 Y)
"""
import re
from typing import Optional


def extract_model_core(model_name: str) -> str:
    """
    모델명에서 핵심 식별자 추출
    
    Examples:
        - 벤츠 E-클래스 W213 → E-클래스
        - 벤츠 GLE-클래스 W167 → GLE-클래스
        - 테슬라 모델 3 → 모델 3
        - 테슬라 모델 Y → 모델 Y
        - 그랜저 IG → 그랜저
        - BMW 3시리즈 → 3시리즈
    """
    model = model_name.strip()
    
    # 벤츠 클래스 패턴 (GLE-클래스, GLC-클래스, E-클래스, S-클래스 등)
    # GL로 시작하는 모델 먼저 체크 (GLE, GLC, GLS, GLB 등)
    benz_gl_match = re.match(r'(GL[ABCES])-?클래스', model, re.IGNORECASE)
    if benz_gl_match:
        return benz_gl_match.group(1).upper() + '-클래스'
    
    # 일반 벤츠 클래스 (A, B, C, E, S 등)
    benz_match = re.match(r'([A-Z])-?클래스', model, re.IGNORECASE)
    if benz_match:
        return benz_match.group(1).upper() + '-클래스'
    
    # BMW 시리즈 패턴 (3시리즈, 5시리즈, X3, X5, i4 등)
    bmw_series = re.match(r'(\d시리즈|[XZiM]\d+)', model, re.IGNORECASE)
    if bmw_series:
        return bmw_series.group(1)
    
    # 테슬라 모델 패턴 (모델 3, 모델 Y, 모델 S, 모델 X)
    tesla_match = re.match(r'(모델\s*[3YSX]|Model\s*[3YSX])', model, re.IGNORECASE)
    if tesla_match:
        # 정규화: "모델 3" 형태로 통일
        matched = tesla_match.group(1)
        letter = matched[-1].upper()
        return f'모델 {letter}'
    
    # 아우디 패턴 (A6, Q5, e-tron, RS 등)
    audi_match = re.match(r'([AQeRS][0-9]+|e-?tron)', model, re.IGNORECASE)
    if audi_match:
        return audi_match.group(1).upper()
    
    # 포르쉐 패턴 (911, 카이엔, 파나메라 등)
    porsche_match = re.match(r'(911|카이엔|파나메라|마칸|타이칸|박스터|카이맨)', model)
    if porsche_match:
        return porsche_match.group(1)
    
    # 일반 모델명: 첫 번째 핵심 단어 (공백/괄호 이전)
    # 그랜저 IG, 쏘나타 DN8, K5 DL3 → 그랜저, 쏘나타, K5
    core_match = re.match(r'^([가-힣A-Za-z0-9]+)', model)
    if core_match:
        return core_match.group(1)
    
    return model


def is_model_match(target_model: str, candidate_model: str) -> bool:
    """
    두 모델이 같은 계열인지 정확히 판단
    
    Args:
        target_model: 사용자가 선택한 모델 (E-클래스, 모델 3 등)
        candidate_model: 데이터셋의 모델명
    
    Returns:
        bool: 같은 계열이면 True
    
    Examples:
        - is_model_match("E-클래스", "E-클래스 W213") → True
        - is_model_match("E-클래스", "GLE-클래스") → False
        - is_model_match("모델 3", "모델 3") → True
        - is_model_match("모델 3", "모델 Y") → False
    """
    target_core = extract_model_core(target_model)
    candidate_core = extract_model_core(candidate_model)
    
    # 정확한 핵심 식별자 매칭
    return target_core.lower() == candidate_core.lower()


def create_model_filter(df, model_column: str, target_model: str):
    """
    DataFrame에 대한 모델 필터 마스크 생성
    
    Args:
        df: pandas DataFrame
        model_column: 모델명 컬럼명
        target_model: 필터링할 대상 모델명
    
    Returns:
        pandas Series (boolean mask)
    """
    return df[model_column].apply(lambda x: is_model_match(target_model, str(x)))
