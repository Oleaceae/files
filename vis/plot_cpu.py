import os 
import matplotlib.pyplot as plt

baseDir = "/Users/Oleaceae/Documents/Work/RTS/archive/2024-11-15@02-28-18"
timestamp_step = 100 # Customize, should be set to the steps in the csv, default be 100ms

exprDate = "20241115" # Customize
exprStartTime = 1731662892000 # Customize
lowerBound = 1731662895000 # Customize
upperBound = 1731662906000 # Customize
longReqTimestamps= [1731662904623 - 96, 1731662903655-97, 1731662900295 - 113, 1731662899777 - 98] # Customize

def work(fname, selFields, lb, ub):
    vals = dict()
    nodeName = f"{fname.split('-')[0]}-{fname.split('-')[1]}"
    with open(os.path.join(baseDir, fname), "r") as f:
        lines = f.readlines()

        # Get _CPU.csv header
        header = []
        for headerField in lines[0].split(" "):
            header.append(headerField.strip())
        
        # Initialize result buffer
        for selField in selFields:
            vals[selField] = dict()
            vals[selField]["timestamp"] = []
            vals[selField]["value"] = []
    
        # Fill in result buffer
        for i in range(1, len(lines)):
            for selField in selFields:
                line = lines[i]
                timestamp = line.split(" ")[0]
                try:
                    timestamp = int(float(timestamp) * 1000)
                except:
                    continue

                # not within range
                if timestamp < lb or timestamp > ub:
                    continue

                colIdx = header.index(selField) 
                vals[selField]["timestamp"].append(timestamp - exprStartTime)
                vals[selField]["value"].append(float(line.split(" ")[colIdx]))

    figsDir = f"cpu_figs"
    os.makedirs(figsDir, exist_ok=True)
    # Plot
    plt.clf()
    for selField in selFields:
        xTime = vals[selField]["timestamp"]
        yUtil = vals[selField]["value"]

        plt.plot(xTime, yUtil, label=selField)
    
    plt.title(f"{nodeName}")
    plt.xlabel("Timestamp")
    plt.ylabel("Utilization (%)")
    # plt.legend()

    # Mark timestamp of long requests
    for longReqTimestamp in longReqTimestamps:
        plt.axvline(x=longReqTimestamp-exprStartTime, color="r")
    # plt.axvline(x=1731646495697-exprStartTime, color="g")

    plt.savefig(os.path.join(figsDir, f"stacked_{nodeName}.png"))


if __name__ == "__main__":
    # _CPU.csv
    fnames = [
        f"node-0-{exprDate}_CPU.csv",
        f"node-1-{exprDate}_CPU.csv",
        f"node-2-{exprDate}_CPU.csv",
        f"node-3-{exprDate}_CPU.csv",
        f"node-4-{exprDate}_CPU.csv",
        f"node-5-{exprDate}_CPU.csv"
    ]
    selFields = []
    for i in range(0, 32):
        selFields.append(f"[CPU:{i}]Totl%")
    # selFields.append(f"[CPU:{1}]Totl%")
    # selFields = [
    #     "[CPU:0]Totl%",
    #     "[CPU:1]Totl%",
    #     "[CPU:2]Totl%",
    #     "[CPU:3]Totl%",
    #     "[CPU:4]Totl%",
    #     "[CPU:5]Totl%",
    #     "[CPU:6]Totl%",
    #     "[CPU:7]Totl%",
    #     "[CPU:8]Totl%"
    # ] # Customize
    for fname in fnames:
        print(fname)
        work(fname, selFields, lowerBound, upperBound)
