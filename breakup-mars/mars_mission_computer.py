import random
import time
import json
import threading
import platform
import psutil

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
    def __init__(self, sensor,setting_file='setting.txt'):
        self.sensor = sensor
        self.env_values = {}
        self.settings = self.load_settings(setting_file)
        self.computer_data = {}

    def get_sensor_data(self):
        global stop_flag
        while not stop_flag:
            self.sensor.set_env()
            self.env_values = self.sensor.get_env()
            print(json.dumps(self.env_values, indent=2))
            time.sleep(5)
        print('Sytem stoped')

    def get_mission_computer_info_and_load(self):
        self.print_selected_info()

    def print_selected_info(self):
        result = {key: self.computer_data.get(key, 'N/A') for key in self.settings}
        print('[Mission Computer Output]')
        print(json.dumps(result, indent=2))
        
def input_cheaker():
    global stop_flag
    while True:
        cmd = input("종료하려면 'q' 입력: \n")
        if cmd.strip().lower() == 'q':
            stop_flag = True
            break



ds=DummySensor() 
RunComputer=MissionComputer(ds)

stop_flag = False

thread2 = threading.Thread(target=RunComputer.get_sensor_data)
thread1 = threading.Thread(target=input_cheaker)

thread1.start()
thread2.start()

thread1.join()
thread2.join()


'''파이썬 코드를 사용해서 다음과 같은 미션 컴퓨터의 정보를 알아보는 메소드를 get_mission_computer_info() 라는 이름으로 만들고 문제 7에서 완성한 MissionComputer 클래스에 추가한다.

- 필요한 미션 컴퓨터의 시스템 정보
운영체계
운영체계 버전
CPU의 타입
CPU의 코어 수
메모리의 크기
get_mission_computer_info()에 가져온 시스템 정보를 JSON 형식으로 출력하는 코드를 포함한다.
미션 컴퓨터의 부하를 가져오는 코드를 get_mission_computer_load() 메소드로 만들고 MissionComputer 클래스에 추가한다
get_mission_computer_load() 메소드의 경우 다음과 같은 정보들을 가져 올 수 있게한다.
CPU 실시간 사용량
메모리 실시간 사용량
get_mission_computer_load()에 해당 결과를 JSON 형식으로 출력하는 코드를 추가한다.
get_mission_computer_info(), get_mission_computer_load()를 호출해서 출력이 잘되는지 확인한다.
MissionComputer 클래스를 runComputer 라는 이름으로 인스턴스화 한다.
runComputer 인스턴스의 get_mission_computer_info(), get_mission_computer_load() 메소드를 호출해서 시스템 정보에 대한 값을 출력 할 수 있도록 한다.
최종적으로 결과를 mars_mission_computer.py 에 저장한다'''