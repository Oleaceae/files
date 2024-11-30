import os
import json
import os
import threading
import time
import random

with open("config.json", "r") as fp:
    config = json.load(fp)


def remote_exec(node, cmd):
    os.system(f"ssh {node} \"{cmd}\"")

def start_collectl():
    print("Starting collectl ...")
    swarm_nodes = config["sysarch"]["swarm_nodes"]
    for node in swarm_nodes:
        remote_exec(node, "hostname")
        remote_exec(node, "rm -rf /tmp/*.raw.gz")
        remote_exec(node, "pkill -u $(whoami) collectl")
        remote_exec(node, "collectl -sCcm  -oTm -f /tmp -i 0.1 > /dev/null 2>&1 < /dev/null &")

def end_collectl():
    print("Ending collectl ...")
    swarm_nodes = config["sysarch"]["swarm_nodes"]
    for node in swarm_nodes:
        remote_exec(node, "hostname")
        remote_exec(node, "pkill -u $(whoami) collectl")

def get_collectl_data():
    print("Getting collectl raw data ...")
    swarm_nodes = config["sysarch"]["swarm_nodes"]
    client_node = config["sysarch"]["client_node"]
    sysdata_dir = "/tmp/sysdata"
    os.makedirs(sysdata_dir, exist_ok=True)
    os.system(f"rm -rf {sysdata_dir}/*.raw.gz")
    for node in swarm_nodes:
        remote_exec(node, "hostname")
        remote_exec(node, f"rsync /tmp/*.raw.gz {client_node}:{sysdata_dir}")
    print(f"Done, sysdata saved to {sysdata_dir}")

def workload():
    seconds = config["wrk"]["seconds"]      # Duration of the test in seconds
    rate_dis = config["wrk"]["rate_dis"]    # Rate distribution, default to be exponential
    rate_avg = config["wrk"]["rate_avg"]    # Avg rate of requests per sec
    thrd_num = config["wrk"]["thrd_num"]    # Number of threads sending requests
    conn_num = config["wrk"]["conn_num"]    # Number of concurrent connections
    print(f"Starting workload for {seconds} s ...")

    lua_script = config["wrk"]["lua_script"] # Path of Lua scripts for request generation
    url = config["wrk"]["url"] # Target URL

    # Create and clear result dir
    result_dir = "/tmp/lat" # logs will be saved to result_node:result_dir
    os.makedirs(result_dir, exist_ok=True)
    os.system(f"rm -rf {result_dir}/*.log")

    # Generate workload, logs saved to lat.log
    os.system(f"../wrk2/wrk -D {rate_dis} -R {rate_avg} -t {thrd_num} -c {conn_num} -d {seconds} -s {lua_script} {url} > /dev/null") 

    print(f"Done, logs saved to {result_dir}")

def stress():
    node = config["stress"]["node"]
    times = config["stress"]["times"]
    seconds = config["stress"]["seconds"]
    cpu = config["stress"]["cpu"]
    vm = config["stress"]["vm"]
    vm_bytes = config["stress"]["vm_bytes"]
    inj_type = config["stress"]["inj_type"] # Fix: given timepoint, Rand: randomly generates
    fix_time = sorted(config["stress"]["fix_time"])

    wrk_duration = config["wrk"]["seconds"]
    stress_time = []
    if inj_type == "rand":
        # Does not stress at the start or the end
        timeslice = wrk_duration / times
        for i in range(times):
            stress_time.append(random.uniform(i*timeslice, (i+1)*timeslice))
    elif inj_type == "fix":
        stress_time = fix_time
    
    for i in range(len(stress_time)):
        if i == 0:
            time.sleep(stress_time[0])
        else:
            time.sleep(stress_time[i] - stress_time[i-1])
        print(f"Injecting millibottleneck at {stress_time[i]} ...")
        remote_exec(node, f"timeout {seconds}s stress --cpu {cpu} --vm {vm} --vm-bytes {vm_bytes}")
   


def vis():
    print("Visualizing request latencies ...")
    os.system("python vis_lat.py")
    print("Visualizing system utilization ...")
    os.system("python vis_sys.py")

if __name__ == "__main__":
    start_collectl()

    thread_wrk = threading.Thread(target=workload)
    thread_sts = threading.Thread(target=stress)
    thread_wrk.start()
    thread_sts.start()

    print("Waiting for workload to complete ...")
    thread_wrk.join()
    thread_sts.join()

    end_collectl()
    get_collectl_data()

    print("Data collecting complete, visualizing result ...")
    vis()
    
    print("All Done")