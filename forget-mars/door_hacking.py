#!/usr/bin/env python3
# door_hacking.py

import zipfile
import zlib
import multiprocessing
import time
import string
import os
from multiprocessing import Value, Queue, Process

os.chdir(os.path.dirname(__file__))
ZIP_PATH = 'emergency_storage_key.zip'
PASSWORD_FILE = 'password.txt'
CHUNK_FACTOR = 6  # 청크 분할 계수


def idx_to_password(idx: int) -> str:
    chars = string.digits + string.ascii_lowercase
    base = len(chars)
    pwd = []
    for _ in range(6):
        idx, rem = divmod(idx, base)
        pwd.append(chars[rem])
    return ''.join(reversed(pwd))


def worker(start_idx: int, end_idx: int, found_flag: Value, result_q: Queue):
    try:
        zf = zipfile.ZipFile(ZIP_PATH)
    except Exception as e:
        print(f"[Worker {start_idx}] ZIP 열기 실패: {e}", flush=True)
        return

    attempts = 0
    log_interval = 100_000  # 테스트용 로그 간격 (필요시 조정)

    for idx in range(start_idx, end_idx):
        # 1,000회마다만 플래그 확인
        if idx % 1000 == 0 and found_flag.value:
            break

        pwd = idx_to_password(idx)
        attempts += 1

        try:
            # 메모리상에서 첫 파일만 읽어서 검사
            first = zf.namelist()[0]
            zf.read(first, pwd=pwd.encode())
            # 성공
            found_flag.value = True
            result_q.put(pwd)
            break
        except (RuntimeError, zlib.error, zipfile.BadZipFile):
            pass

        if attempts % log_interval == 0:
            elapsed = time.time() - START_TIME.value
            print(f"[Worker {start_idx}] {attempts}회 시도, 경과: {elapsed:.1f}s", flush=True)

    zf.close()


def save_password(pwd: str):
    try:
        with open(PASSWORD_FILE, 'w') as f:
            f.write(pwd)
        print(f"✔ 비밀번호 '{pwd}'를 '{PASSWORD_FILE}'에 저장했습니다.")
    except Exception as e:
        print(f"비밀번호 저장 실패: {e}")


if __name__ == '__main__':
    TOTAL = 36 ** 6
    cpu_count = multiprocessing.cpu_count()
    chunk_size = (TOTAL + cpu_count * CHUNK_FACTOR - 1) // (cpu_count * CHUNK_FACTOR)

    found_flag = Value('b', False, lock=False)
    result_q = Queue()
    START_TIME = Value('d', time.time(), lock=False)

    processes = []
    for i in range(cpu_count * CHUNK_FACTOR):
        start = i * chunk_size
        end = min(start + chunk_size, TOTAL)
        if start >= end:
            break
        p = Process(target=worker, args=(start, end, found_flag, result_q))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    password = None
    if not result_q.empty():
        password = result_q.get()

    if password:
        elapsed = time.time() - START_TIME.value
        print(f"\n🎉 비밀번호를 찾았습니다: '{password}' (총 경과 {elapsed:.1f}s)")
        save_password(password)
    else:
        print("\n❌ 비밀번호를 찾지 못했습니다.")