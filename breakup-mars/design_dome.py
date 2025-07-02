import numpy as np
import glob

paths = glob.glob("question5/*.csv")
CSVdata = []
answer=[]

for path in paths:
    arr = np.genfromtxt(path, delimiter=",", dtype=None, encoding="utf-8", names=True)
    CSVdata.append(arr)

merged = np.concatenate(CSVdata)

part_key = '\ufeffparts'
value_key = 'strength'

unique_parts = np.unique(merged[part_key])
for part in unique_parts:
    mask = merged[part_key] == part
    values = merged[value_key][mask]
    avg = np.mean(values)
    if avg<=50:
        answer.append(avg)
np.array(avg)
np.savetxt("parts_to_work_on.csv", answer,delimiter=',', fmt="%.2f")