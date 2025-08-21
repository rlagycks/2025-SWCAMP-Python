#!/usr/bin/env python3
# door_hacking.py

import zipfile
import time
import string
import multiprocessing
import os
import zlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(SCRIPT_DIR, 'emergency_storage_key.zip')
PASSWORD_FILE = os.path.join(SCRIPT_DIR, 'password.txt')

CHARSET = string.digits + string.ascii_lowercase
PASSWORD_LENGTH = 6

def generate_password(index: int) -> str:
    """정수 인덱스를 기반으로 6자리 비밀번호를 생성합니다."""
    base = len(CHARSET)
    password_chars = []
    
    temp_index = index
    for _ in range(PASSWORD_LENGTH):
        temp_index, remainder = divmod(temp_index, base)
        password_chars.append(CHARSET[remainder])
    
    return "".join(reversed(password_chars))

def worker(start_idx: int, end_idx: int, found_flag: multiprocessing.Value, result_q: multiprocessing.Queue, start_time: float):
    """
    각 프로세스가 실행할 작업 함수.
    주어진 범위 내의 인덱스를 암호로 변환하여 암호 풀기를 시도합니다.
    """
    try:
        zip_file = zipfile.ZipFile(ZIP_PATH)
        first_file_in_zip = zip_file.namelist()[0]
    except FileNotFoundError:
        print(f"[Worker {os.getpid()}] 오류: ZIP 파일 '{ZIP_PATH}'을(를) 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"[Worker {os.getpid()}] 오류: ZIP 파일을 여는 중 문제 발생 - {e}")
        return

    attempts_in_worker = 0
    for idx in range(start_idx, end_idx):
        if idx % 1000 == 0:
            if found_flag.value:
                break

        password = generate_password(idx)
        attempts_in_worker += 1

        try:
            zip_file.read(first_file_in_zip, pwd=password.encode('utf-8'))
            
            with found_flag.get_lock():
                found_flag.value = True
            result_q.put(password)
            
            elapsed_time = time.time() - start_time
            print(f"\n[Worker {os.getpid()}] 암호 발견! 시도 횟수: {attempts_in_worker}회, 진행 시간: {elapsed_time:.2f}초")
            break
            
        except (RuntimeError, zlib.error, zipfile.BadZipFile):
            continue
        except Exception as e:
            print(f"[Worker {os.getpid()}] 암호 시도 중 예외 발생: {e}")
            continue
            
    zip_file.close()

def unlock_zip():
    start_time = time.time()
    total_passwords = len(CHARSET) ** PASSWORD_LENGTH
    
    try:
        cpu_count = multiprocessing.cpu_count()
    except NotImplementedError:
        cpu_count = 4

    chunk_size = total_passwords // cpu_count
    found_flag = multiprocessing.Value('b', False)
    result_q = multiprocessing.Queue()

    print("--- 암호 해독 시작 ---")
    print(f"시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"총 시도할 암호 수: {total_passwords:,}개")
    print(f"워커 프로세스 수: {cpu_count}개")
    print("---------------------\n")

    processes = []
    for i in range(cpu_count):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size if i < cpu_count - 1 else total_passwords
        
        process = multiprocessing.Process(target=worker, args=(start_index, end_index, found_flag, result_q, start_time))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    end_time = time.time()
    total_elapsed_time = end_time - start_time

    if not result_q.empty():
        found_password = result_q.get()
        print("\n--- 결과 ---")
        print(f"암호 해독 성공!")
        print(f"찾은 암호: {found_password}")
        print(f"총 소요 시간: {total_elapsed_time:.2f}초")
        
        try:
            with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write(found_password)
            print(f"암호를 '{PASSWORD_FILE}' 파일에 성공적으로 저장했습니다.")
        except IOError as e:
            print(f"오류: 암호 파일 저장에 실패했습니다 - {e}")
    else:
        print("\n--- 결과 ---")
        print(f" 암호 해독 실패. (총 소요 시간: {total_elapsed_time:.2f}초)")


if __name__ == '__main__':
    if not os.path.exists(ZIP_PATH):
        print(f"오류: '{ZIP_PATH}' 파일을 찾을 수 없습니다.")
        print("스크립트와 동일한 폴더에 암호화된 zip 파일을 위치시켜 주세요.")
    else:
        unlock_zip()
