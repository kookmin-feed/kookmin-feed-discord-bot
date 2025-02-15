import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """로거를 설정하고 반환합니다."""
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있다면 추가 설정하지 않음
    if logger.handlers:
        return logger
        
    # 로그 레벨 설정
    logger.setLevel(logging.INFO)
    
    # 로그 포맷 설정
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # stdout 핸들러 (INFO 레벨)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    
    # stderr 핸들러 (ERROR 레벨)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    
    return logger 