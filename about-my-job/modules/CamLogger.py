"""
파이썬 기본 logger 사용
참고자료 1 : https://docs.python.org/ko/3.11/howto/logging.html (공식 문서)
참고자료 2 : https://jh-bk.tistory.com/40 (일반 블로그)
"""
import logging
from datetime import datetime

now = datetime.now()
now = now.strftime("%y%m%d")

# 로거 객체 생성 및 설정
log_path = "./logs"
cam_logger = logging.getLogger(__name__) # 로거가 사용되는 네임스페이스를 따름
cam_logger.setLevel(logging.INFO) # 기본 INFO level 까지 로깅 (필요시 개별 파일마다 별도로 로그 레벨 설정가능)

# 일반 로깅
formatter = logging.Formatter("%(asctime)s %(levelname)s : %(processName)s %(threadName)s %(funcName)s() -> %(message)s")
file_handler = logging.FileHandler(f"{log_path}/{now}_cam_events.log")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# 크리티컬 로깅
critical_formatter = logging.Formatter("!!!CRITICAL!!! %(asctime)s %(levelname)s : %(processName)s %(threadName)s %(funcName)s -> %(message)s")
critical_file_handler = logging.FileHandler(f"{log_path}/{now}_cam_critical_events.log")
critical_file_handler.setFormatter(critical_formatter)
critical_file_handler.setLevel(logging.CRITICAL) # 크리티컬만 수집
critical_stream_handler = logging.StreamHandler()
critical_stream_handler.setFormatter(critical_formatter)
critical_stream_handler.setLevel(logging.CRITICAL) # 크리티컬만 수집

# 로거에 부착
cam_logger.addHandler(file_handler)
cam_logger.addHandler(stream_handler)
cam_logger.addHandler(critical_file_handler)
cam_logger.addHandler(critical_stream_handler)
