import random
import time
import json
import threading

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
    def __init__(self, sensor):
        self.sensor = sensor
        self.env_values = {}

    def get_sensor_data(self):
        global stop_flag
        while not stop_flag:
            self.sensor.set_env()
            self.env_values = self.sensor.get_env()
            print(json.dumps(self.env_values, indent=2))
            time.sleep(5)
        print('Sytem stoped')
        
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