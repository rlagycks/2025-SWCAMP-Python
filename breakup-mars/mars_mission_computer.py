import random
import time
import json
import threading
import platform
import psutil
import multiprocessing
import signal
import sys
import termios
import tty
import select
import os

os.chdir(os.path.dirname(__file__))
stop_event = threading.Event()

def _sigint_handler(signum, frame):
    stop_event.set()

signal.signal(signal.SIGINT, _sigint_handler)

def watch_q_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        while not stop_event.is_set():
            r, _, _ = select.select([sys.stdin], [], [], 1)
            if r:
                ch = sys.stdin.read(1)
                if ch.lower() == 'q':
                    stop_event.set()
                    break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

class DummySensor:
    def __init__(self):
        self.env_values = {
            "internal_temperature": 0,
            "external_temperature": 0,
            "external_illuminance": 0,
            "internal_co2": 0.0,
            "internal_oxygen": 0
        }

    def set_env(self):
        self.env_values["internal_temperature"] = random.randint(18, 31)
        self.env_values["external_temperature"] = random.randint(0, 22)
        self.env_values["external_illuminance"] = random.randint(500, 715)
        self.env_values["internal_co2"] = round(random.uniform(0.02, 0.1), 3)
        self.env_values["internal_oxygen"] = random.randint(4, 8)

    def get_env(self):
        return self.env_values

class MissionComputer:
    def __init__(self, sensor, setting_file='setting.txt'):
        self.sensor = sensor
        try:
            self.settings = self._load_settings(setting_file)
        except FileNotFoundError:
            print(f"설정 파일을 찾을 수 없습니다: {setting_file}")
            self.settings = []
        except Exception as e:
            print(f"설정 로드 중 오류: {e}")
            self.settings = []
        self._init_computer_data()

    def _load_settings(self, setting_file):
        with open(setting_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def _init_computer_data(self):
        self.computer_data = {
            'os': platform.system,
            'os_version': platform.version,
            'cpu_type': platform.processor,
            'cpu_cores': lambda: psutil.cpu_count(logical=False),
            'memory_total': lambda: f"{psutil.virtual_memory().total // (1024**2)} MB",
            'cpu_usage': lambda: f"{psutil.cpu_percent(interval=1)} %",
            'memory_usage': lambda: f"{psutil.virtual_memory().percent} %"
        }

    def get_mission_computer_info_once(self):
        keys = ['os', 'os_version', 'cpu_type', 'cpu_cores', 'memory_total']
        result = {
            k: (self.computer_data[k]() if callable(self.computer_data[k]) else self.computer_data[k])
            for k in keys
        }
        print('[Info ]', json.dumps(result, indent=2))

    def get_mission_computer_load_once(self):
        keys = ['cpu_usage', 'memory_usage']
        result = {k: self.computer_data[k]() for k in keys}
        print('[Load ]', json.dumps(result, indent=2))

    def get_sensor_data(self):
        while not stop_event.is_set():
            self.sensor.set_env()
            vals = self.sensor.get_env()
            print('[Sensor]', json.dumps(vals, indent=2))
            time.sleep(5)

def info_loop(mc: MissionComputer):
    while not stop_event.is_set():
        try:
            mc.get_mission_computer_info_once()
        except Exception as e:
            print("Info 에러:", e)
        time.sleep(20)

def load_loop(mc: MissionComputer):
    while not stop_event.is_set():
        try:
            mc.get_mission_computer_load_once()
        except Exception as e:
            print("Load 에러:", e)
        time.sleep(20)

def start_mc(instance_id: int):
    ds = DummySensor()
    mc = MissionComputer(ds)

    threads = [
        threading.Thread(target=info_loop, args=(mc,), daemon=True),
        threading.Thread(target=load_loop, args=(mc,), daemon=True),
        threading.Thread(target=mc.get_sensor_data, daemon=True),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == '__main__':
    # 'q' 키 감시 스레드 띄우기
    threading.Thread(target=watch_q_key, daemon=True).start()

    # 3개 독립 프로세스 생성
    processes = []
    for i in (1, 2, 3):
        p = multiprocessing.Process(target=start_mc, args=(i,))
        p.start()
        processes.append(p)

    # 자식 프로세스 완료 대기
    for p in processes:
        p.join()

    print("모든 MissionComputer 프로세스가 종료되었습니다.")

    '''
    
    '''