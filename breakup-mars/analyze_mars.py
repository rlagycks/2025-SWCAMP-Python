import os
from pprint import pprint

os.chdir(os.path.dirname(__file__))
inventory=[]
try:
    with open('Mars_Base_Inventory_List.csv', 'r', encoding='utf-8') as f:
        mars_logs = f.readlines()

except FileNotFoundError:
    print("로그 파일이 존재하지 않습니다.")
    exit(1)
except PermissionError:
    print("로그 파일에 접근 권한이 없습니다.")
    exit(1)

header = mars_logs[0].strip().split(',')

for line in mars_logs[1:]:
    values = line.strip().split(',')
    if len(values) == len(header):
        record = dict(zip(header, values))
        inventory.append(record)

inventory.sort(key=lambda x: float(x['Flammability']))

flammable_items = [item for item in inventory if float(item['Flammability']) >= 0.7]
for item in flammable_items:
    print(item)
with open('flammable_items.csv', 'w', encoding='utf-8') as f:
    f.write(','.join(flammable_items[0].keys()) + '\n')
    for item in flammable_items:
        f.write(','.join(item.values()) + '\n')