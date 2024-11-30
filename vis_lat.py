import os
import numpy as np
import matplotlib.pyplot as plt

png_dir = "./vis"


lats = []
sts = {}
sts_lat = {}
eds = {}
log_dir = "/tmp/lat"
for log_fname in os.listdir(log_dir):
    print(f"Processing {log_fname}")
    with open(os.path.join(log_dir, log_fname), "r") as fp:
        lines = fp.readlines()
    for line in lines:
        line_split = line.split()

        st = round(float(line_split[0]) * 1000)
        lat = round(float(line_split[1]) * 1000)
        ed = st + lat

        lats.append(lat)

        if st not in sts:
            sts[st] = 0
            sts_lat[st] = 0
        if ed not in eds:
            eds[ed] = 0

        sts[st] += 1
        sts_lat[st] += lat
        eds[ed] += 1

# Latency frequency bar plot
lat_max = max(lats)
lat_min = min(lats)
lat_gap = lat_max-lat_min+1

lat_freqs = np.zeros(lat_gap)
for lat in lats:
    lat_freqs[lat-lat_min] += 1    

plt.clf()
plt.bar(range(lat_min, lat_max+1), lat_freqs)
plt.xlabel("Latency (ms)")
plt.title("Latency Frequency Distribution")
plt.savefig(f"{png_dir}/lat_freqs.png")
print(f"Min latency {lat_min}, max latency {lat_max}")


# queue_len
plt.clf()
time_lb = min(sts.keys())
time_ub = max(eds.keys())
timespan = time_ub - time_lb
print(f"Start timestamp: {time_lb}, end timestamp: {time_ub}, total: {timespan}ms")

queue_len = []
started = 0
ended = 0
for t in range(time_lb, time_ub+1):
    if t in sts:
        started += sts[t]

    if t in eds:
        ended += eds[t]

    queue_len.append(started - ended)

plt.plot(range(0, timespan+1), queue_len)
plt.xlabel("Timeline")
plt.title("Queue Length")
plt.savefig(f"{png_dir}/queue_len.png")

# requests starting timeline
plt.clf()
sts_filled = []
for t in range(time_lb,time_ub+1):
    if t in sts:
        sts_filled.append(sts[t])
    else:
        sts_filled.append(0)

plt.plot(range(0, timespan+1), sts_filled)
plt.xlabel("Timeline")
plt.title("Requests Starting Timeline")
plt.savefig(f"{png_dir}/req_st_timeline.png")

# Latency timeline
plt.clf()
sts_lat_filled = []
for t in range(time_lb, time_ub+1):
    if t in sts_lat:
        sts_lat_filled.append(sts_lat[t] / sts[t])
    else:
        sts_lat_filled.append(0)
plt.plot(range(0, timespan+1), sts_lat_filled)
plt.xlabel("Timeline")
plt.ylabel("Average latency (ms)")
plt.title("Average Latency Timeline")
plt.savefig(f"{png_dir}/avg_lat_timeline.png")

print("Done")