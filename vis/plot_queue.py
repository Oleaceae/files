import os
import numpy as np
import matplotlib.pyplot as plt

longReqTimestamps= [1731662904623 - 96, 1731662903655-97, 1731662900295 - 113, 1731662899777 - 98]

resDir = "/Users/Oleaceae/Documents/Work/RTS/archive/2024-11-15@02-28-18"

exprFName = "Experiments_timestamp.log"
resultFName = "result_post.jtl"

exprSTime = -1
exprETime = -1
with open(os.path.join(resDir, exprFName), "r") as f:
    lines = f.readlines()
    exprSTime = int(lines[2])
    exprETime = int(lines[3])

print(exprSTime, exprETime)

lb = 1731662895000
ub = 1731662906000
# lb = exprSTime
# ub = exprETime
win_size = 50
num_win = (ub-lb) // win_size

win_st = np.zeros(num_win)
win_ed = np.zeros(num_win)
req_num = 0
with open(os.path.join(resDir, resultFName), "r") as f:
    lines = f.readlines()
    for i in range(len(lines)):
        line = lines[i]
        timestamp = line.split(" ")[0]
        try:
            timestamp = int(timestamp)
        except:
            #print("Err field val: ", timestamp)
            continue
    
        if timestamp < lb or timestamp > ub:
            continue        

        latency = int(line.split(" ")[1])

        ed = timestamp - lb
        st = timestamp - latency - lb

        win_st[st // win_size] += 1
        win_ed[ed // win_size] += 1
        req_num += 1

print(req_num)

q = []
num_st = 0
num_rt = 0
for i in range(num_win):
    num_st += win_st[i]
    num_rt += win_ed[i]
    q.append(num_st - num_rt)

plt.plot(list(range(num_win)), q)

for longReqTimestamp in longReqTimestamps:
    plt.axvline(x=(longReqTimestamp - lb) // win_size, color="r")

plt.show()

