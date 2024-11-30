import subprocess
import os
import matplotlib.pyplot as plt
import json

with open("config.json", "r") as fp:
    config = json.load(fp)

png_dir = config["vis"]["png_dir"]
for node in config["vis"]["sysdata_vis_nodes"]:
    print(f"Visualizing {node} sysdata ...")
    # Extract from collectl raw.gz
    sysdata_path = f"/tmp/sysdata/{node}*.raw.gz"
    extract_cmd = f"collectl -p  {sysdata_path} --verbose -sCcm -oTm"
    res = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)
    records = res.stdout.split("RECORD")

    timestamps = []

    cpu_user = []
    cpu_sys = []
    cpu_wait = []
    cpu_idle = []

    # Not used currently
    cpus_single_user = []
    cpus_single_sys = []
    cpus_single_wait = []
    cpus_single_idle  = []

    mem_used = []
    mem_free = []

    for record in records[1:]:
        record_lines = record.splitlines()

        timestamp = record_lines[0].strip().split(" ")[4][1:-1]
        timestamps.append(timestamp)

        cpu_data = record_lines[4].strip().split()
        cpu_user.append(int(cpu_data[0]))
        cpu_sys.append(int(cpu_data[2]))
        cpu_wait.append(int(cpu_data[3]))
        cpu_idle.append(int(cpu_data[9]))

        cpu_single_user = []
        cpu_single_sys = []
        cpu_single_wait = []
        cpu_single_idle = []
        cpu_num = int(cpu_data[10])
        for i in range(8, 8 + cpu_num):
            single_cpu_data = record_lines[i].strip().split()
            cpu_single_user.append(single_cpu_data[1])
            cpu_single_sys.append(single_cpu_data[3])
            cpu_single_wait.append(single_cpu_data[4])
            cpu_single_idle.append(single_cpu_data[10])

        cpus_single_user.append(cpu_single_user)
        cpus_single_sys.append(cpu_single_sys)
        cpus_single_wait.append(cpu_single_wait)
        cpus_single_idle.append(cpu_single_idle)

        mem_idx = 8 + cpu_num + 4
        mem_data = record_lines[mem_idx].strip().split()
        mem_used.append(int(mem_data[1][:-1]) / int(mem_data[0][:-1]))
        mem_free.append(int(mem_data[2][:-1]) / int(mem_data[0][:-1]))

    # Visualization
    duration = len(timestamps)

    # CPU Overall utilization
    cpu_used = [cpu_user[i] + cpu_sys[i] + cpu_wait[i] for i in range(duration)]
    plt.clf()
    plt.plot(range(duration), cpu_used, label="Used")
    # plt.plot(range(duration), cpu_idle, label="Idle")
    plt.xlabel("Timeline")
    # plt.legend()
    plt.title("CPU Overall Utilization")
    plt.savefig(f"{png_dir}/cpu_util_{node}.png")

    # Mem Utilization
    plt.clf()
    plt.plot(range(duration), mem_used, label="Used")
    plt.plot(range(duration), mem_free, label="Free")
    plt.xlabel("Timeline")
    plt.legend()
    plt.title("Memory Utilization")
    plt.savefig(f"{png_dir}/mem_util_{node}.png")
