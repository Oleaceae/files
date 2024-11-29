from fabric import ThreadingGroup
import os

# ------------Configuration Start------------
home_dir = os.path.expanduser("~")
work_dir = f"{home_dir}/DeathStarBench/socialNetwork"

test_duration = 1   # Duration of the test in seconds
rate_dis = "exp"    # Rate distribution, default to be exponential
rate_avg = 1      # Avg rate of requests per sec
thread_num = 1      # Number of threads sending requests
connection_num = 1  # Number of concurrent connections

lua_script = f"{home_dir}/DeathStarBench/socialNetwork/wrk2/scripts/social-network/compose-post.lua" # ABSOLUTE path of Lua scripts for request generation
url = "http://localhost:8080/wrk2-api/post/compose" # Target URL

client_nodes= [f'node-{idx}' for idx in range(0, 1)] # ssh of hostnames
result_node = "node-0"
result_dir = f"/result/tmp"

# -------------Configuration END--------------

with ThreadingGroup(*client_nodes) as client_grp:
    # Create and clear result dir
    client_grp.run(f"sudo mkdir -p {result_dir}")
    client_grp.run(f"sudo rm -rf {result_dir}/lat_*.log")

    # Generate and copy logs
    workgen_cmd = f"{work_dir}/../wrk2/wrk -D {rate_dis} -R {rate_avg} -t {thread_num} -c {connection_num} -d {test_duration} -L -s {lua_script} {url}"
    print(workgen_cmd)
    client_grp.run(workgen_cmd)  # Content saved to lat_{hostname}.log
    copy_cmd = f"rsync -P {work_dir}/lat*.log {result_node}:/tmp/result"
    client_grp.run(copy_cmd)     # Copy log to result_dir in result_node

print(f"Done, result saved to {result_dir} of {result_node}")
