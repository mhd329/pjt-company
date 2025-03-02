import os
from concurrent.futures import ProcessPoolExecutor, Future


PROCESS_WORKERS = 4
PROCESS_EXECUTOR = ProcessPoolExecutor(max_workers=PROCESS_WORKERS)
DEBUG = os.getenv("DEBUG") == "True"