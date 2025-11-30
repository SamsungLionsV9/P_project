"""
API 응답 표준화 유틸리티
========================
모든 API 응답을 일관된 형식으로 래핑
"""
from datetime import datetime
from typing import Any, Optional, Dict
from pydantic import BaseModel


class APIResponse(BaseModel):
    """표준 API 응답 스키마"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.now().isoformat()
        super().__init__(**data)


def success_response(data: Any = None, message: str = None) -> Dict:
    """성공 응답 생성"""
    return APIResponse(
        success=True,
        data=data,
        message=message
    ).model_dump()


def error_response(error: str, message: str = None) -> Dict:
    """에러 응답 생성"""
    return APIResponse(
        success=False,
        error=error,
        message=message or error
    ).model_dump()


def paginated_response(
    items: list,
    total: int,
    page: int = 1,
    limit: int = 10,
    message: str = None
) -> Dict:
    """페이지네이션 응답 생성"""
    return APIResponse(
        success=True,
        data={
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        },
        message=message
    ).model_dump()
