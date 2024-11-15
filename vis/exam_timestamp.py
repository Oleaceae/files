import os

resDir = "/Users/Oleaceae/Documents/Work/RTS/archive/2024-11-15@02-28-18"

exprFName = "Experiments_timestamp.log"
resultFName = "result.jtl"

exprSTime = -1
exprETime = -1

minVal = int(1e15)
minIdx = -1
maxVal = 0
maxIdx = -1

with open(os.path.join(resDir, exprFName), "r") as f:
    lines = f.readlines()
    exprSTime = int(lines[2])
    exprETime = int(lines[3])


with open(os.path.join(resDir, resultFName), "r") as f:
    lines = f.readlines()
    for i in range(len(lines)):
        line = lines[i]
        d1 = line.split(" ")[0]
        try:
            timestamp = int(d1)
        except:
            print("Err field val: ", d1)
            continue
        
        if timestamp > maxVal:
            maxVal = timestamp
            maxIdx = i

        
        if timestamp < minVal:
            minVal = timestamp
            minIdx = i
print("Expr start time:\t", exprSTime)
print("Min timestamp:\t\t", minVal, "\t", minIdx)
print()
print("Expr end time:\t\t", exprETime)
print("Max timestamp:\t\t", maxVal, "\t", maxIdx)
print()
print("Req start diff:\t\t", minVal - exprSTime)
print("Req end diff:\t\t", exprETime - maxVal)
