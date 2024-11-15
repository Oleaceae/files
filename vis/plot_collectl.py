import os 
import matplotlib.pyplot as plt

baseDir = "/Users/Oleaceae/Documents/Work/RTS/archive/2024-11-15@02-28-18"
timestamp_step = 100 # Customize, should be set to the steps in the csv, default be 100ms

exprStartTime = 1731662892000 # Customize
lowerBound = 1731662895000 # Customize
upperBound = 1731662906000 # Customize
longReqTimestamps= [1731662904623 - 96, 1731662903655-97, 1731662900295 - 113, 1731662899777 - 98] # Customize

def work(fnames, selField, lb, ub):
    vals = dict()
    for fname in fnames:
        nodeName = f"{fname.split('-')[0]}-{fname.split('-')[1]}"
        with open(os.path.join(baseDir, fname), "r") as f:
            lines = f.readlines()

            # Get _collectl.csv header
            header = []
            for headerField in lines[0].split(" "):
                header.append(headerField.strip())
            colIdx = header.index(selField)
            
            # Initialize result buffer
            vals[nodeName] = dict()
            vals[nodeName]["timestamp"] = []
            vals[nodeName]["value"] = []
        
            # Fill in result buffer
            for i in range(1, len(lines)):
                line = lines[i]
                timestamp = line.split(" ")[0]
                try:
                    timestamp = int(float(timestamp) * 1000)
                except:
                    continue

                # not within range
                if timestamp < lb or timestamp > ub:
                    continue

                vals[nodeName]["timestamp"].append(timestamp-exprStartTime)
                vals[nodeName]["value"].append(float(line.split(" ")[colIdx]))

    figsDir = f"collectl_figs"
    os.makedirs(figsDir, exist_ok=True)
    # Plot
    plt.clf()
    for fname in fnames:
        nodeName = f"{fname.split('-')[0]}-{fname.split('-')[1]}" 
        xTime = vals[nodeName]["timestamp"]
        yUtil = vals[nodeName]["value"]

        plt.plot(xTime, yUtil, label=nodeName)
    
    plt.title(f"{selField}")
    plt.xlabel("Timestamp")
    plt.ylabel("Utilization (%)")
    plt.legend()

    # Mark timestamp of long requests
    for longReqTimestamp in longReqTimestamps:
        plt.axvline(x=longReqTimestamp-exprStartTime, color="r")

    plt.savefig(os.path.join(figsDir, f"stacked_{selField}.png"))


if __name__ == "__main__":
    exprDate = "20241115" # Customize

    # _collectl.csv
    fnames = [
        f"node-0-{exprDate}_collectl.csv",
        f"node-1-{exprDate}_collectl.csv",
        f"node-2-{exprDate}_collectl.csv",
        f"node-3-{exprDate}_collectl.csv",
        f"node-4-{exprDate}_collectl.csv",
        f"node-5-{exprDate}_collectl.csv"
    ]
    selFields = ["[CPU]Totl%", "[MEM]Tot"]
    # selFields = ["[DSK]ReadTot", "[DSK]WriteTot"]
    for selField in selFields:
        print(selField)
        work(fnames, selField, lowerBound, upperBound)
