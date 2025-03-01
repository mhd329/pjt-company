import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future


THREAD_WORKERS = 2
PROCESS_WORKERS = 4
THREAD_EXECUTOR = ThreadPoolExecutor(max_workers=THREAD_WORKERS)
PROCESS_EXECUTOR = ProcessPoolExecutor(max_workers=PROCESS_WORKERS)
DEBUG = os.getenv("DEBUG") == "True"