import os
import numpy as np
import matplotlib.pyplot as plt

resDir = "/users/wbcheng/socialNetwork/2023-0408-WL5000-readHomeTimeline/2024-11-15@14-50-52"

resultFName = "result.jtl"
figDir = "lat_figs"

exprFName = "Experiments_timestamp.log"
exprSTime = -1
exprETime = -1
with open(os.path.join(resDir, exprFName), "r") as f:
    lines = f.readlines()
    exprSTime = int(lines[2])
    exprETime = int(lines[3])


timestamps = dict()
respTimes = dict()

with open(os.path.join(resDir, resultFName), "r") as f:
    lines = f.readlines()
    for line in lines:
        timestamp = line.split(" ")[0]
        try:
            timestamp = int(timestamp)
        except:
            print("Err field val: ", timestamp)
            continue

        respTime = int(line.split(" ")[1])
        reqType = line.split(" ")[2]

        if reqType not in respTimes:
            timestamps[reqType] = []
            respTimes[reqType] = []

        timestamps[reqType].append(timestamp - exprSTime)
        respTimes[reqType].append(respTime)

print("\nRequest Types: ")
os.makedirs(figDir, exist_ok=True)
for reqType in respTimes:
    print(reqType)
    
    plt.clf()
    plt.scatter(timestamps[reqType], respTimes[reqType])

    plt.xlabel("Timestamp")
    plt.ylabel("Latency (ms)")
    plt.title(f"Latency ({reqType})") 


    plt.savefig(os.path.join(figDir, f"lat_dist_{reqType}.png"))


