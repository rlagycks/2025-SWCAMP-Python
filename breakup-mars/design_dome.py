import numpy as np
import glob
import csv

paths = glob.glob("question5/*.csv")
CSVdata = []
answer=[]

for path in paths:
    arr = np.genfromtxt(path, delimiter=",", dtype=None, encoding="utf-8", names=True)
    CSVdata.append(arr)

merged = np.concatenate(CSVdata)

unique_parts = np.unique(merged['\ufeffparts'])
for part in unique_parts:
    mask = merged['\ufeffparts'] == part
    values = merged['strength'][mask]
    avg = np.mean(values)
    if avg<=50:
        answer.append((part,round(avg,2)))
np.array(avg)
with open("parts_to_work_on.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["part", "avg_strength"])  # 헤더
    writer.writerows(answer)

parts2=np.genfromtxt(path,delimiter=',', dtype=str, encoding="utf-8", skip_header=1)
parts3=parts2.T
print(parts3)
