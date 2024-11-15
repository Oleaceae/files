import os
import numpy as np
import matplotlib.pyplot as plt

resDir = "/Users/Oleaceae/Documents/Work/RTS/archive/2024-11-15@02-28-18"

resultFName = "result.jtl"
figDir = "lat_dist_figs"


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
            respTimes[reqType] = []

        respTimes[reqType].append(respTime)

print("\nRequest Types: ")
os.makedirs(figDir, exist_ok=True)
for reqType in respTimes:
    print(reqType)
    freq = dict()
    for respTime in respTimes[reqType]:
        if respTime not in freq:
            freq[respTime] = 0
        freq[respTime] += 1
    
    freq = {k: freq[k] for k in sorted(freq)}
    xRespTime = list(freq.keys())
    yFreq = np.array(list(freq.values()))
    
    plt.clf()
    plt.bar(xRespTime, yFreq)

    plt.xlabel("Latency (ms)")
    plt.ylabel("Frequency")
    plt.title(f"Latency Distribution ({reqType})") 

    maxY = 100 # y-axis values should not exceed maxY
    plt.ylim(0, maxY)

    overflow = yFreq > maxY
    for i in range(len(yFreq)):
        if overflow[i]:
            plt.text(xRespTime[i], 100 + 3.5 * i, yFreq[i], horizontalalignment='center',  fontsize=8, color="r")
        

    plt.savefig(os.path.join(figDir, f"lat_dist_{reqType}.png"))


