import os
from concurrent.futures import ProcessPoolExecutor, Future


SECRET_KEY = os.getenv("SECRET_KEY")
APP_NAME = "WAIS Live CAM"
APP_VERSION = "1.0.0"


PROCESS_WORKERS = 4
PROCESS_EXECUTOR = ProcessPoolExecutor(max_workers=PROCESS_WORKERS)
DEBUG = os.getenv("DEBUG") == "True"