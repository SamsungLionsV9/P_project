"""
Car-Sentix 통합 로깅 시스템
==============================
- 파일 + 콘솔 동시 출력
- 레벨별 컬러 출력
- 일별 로그 파일 롤링
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 로그 디렉토리 생성
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)


class ColorFormatter(logging.Formatter):
    """콘솔 출력용 컬러 포맷터"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str = 'car_sentix', level: str = 'INFO') -> logging.Logger:
    """로거 설정"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 콘솔 핸들러 (컬러 출력)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter(
        '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (일반 텍스트)
    log_file = os.path.join(LOG_DIR, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s %(name)s (%(filename)s:%(lineno)d): %(message)s'
    ))
    logger.addHandler(file_handler)
    
    return logger


# 기본 로거 인스턴스
logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    """모듈별 로거 획득"""
    return setup_logger(f'car_sentix.{name}')
