import os

resDir = "/Users/Oleaceae/Documents/Work/RTS/archive/2024-11-15@02-28-18"

resultFName = "result.jtl"

filterReqType = "StoriesOfTheDay"
filterThresh = 90

print(f"Find {filterReqType} reqs with latency > {filterThresh}: ")
print("Latency\tIndex\tETime\tAPI")
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

        respTime = int(line.split(" ")[1])
        reqType = line.split(" ")[2]
        api = line.split(" ")[3]
        if reqType == filterReqType and respTime > filterThresh: 
            print(f"{respTime} {i} {timestamp} {api}")
