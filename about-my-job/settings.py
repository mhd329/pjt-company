import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future


MAX_WORKERS = 4
THREAD_EXECUTOR = ThreadPoolExecutor(max_workers=MAX_WORKERS)
PROCESS_EXECUTOR = ProcessPoolExecutor(max_workers=MAX_WORKERS)
DEBUG = os.getenv("DEBUG") == "True"