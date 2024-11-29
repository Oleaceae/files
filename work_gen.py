from fabric import ThreadingGroup
import os

# ------------Configuration Start------------
work_dir = "~/DeathStarBench/socialNetwork"

test_duration = 1   # Duration of the test in seconds
rate_dis = "exp"    # Rate distribution, default to be exponential
rate_avg = 1000      # Avg rate of requests per sec
thread_num = 1      # Number of threads sending requests
connection_num = 1  # Number of concurrent connections

lua_script = "./wrk2/scripts/social-network/compose-post.lua" # Lua scripts for request generation
url = "http://localhost:8080/wrk2-api/post/compose" # Target URL

client_hostname = [[f'node-{idx}' for idx in range(6, 6+5)]]
result_node = "node-0"
workgen_cmd = f"../wrk2/wrk -D {rate_dis} -R {rate_avg} -t {thread_num} -c {connection_num} -d {test_duration} -L -s {lua_script} {url}"
copy_cmd = f"rsync -rP ./lat*.log {result_node}:/tmp/result"
# -------------Configuration END--------------

os.system("rm -rf /tmp/result/*")
os.chdir(work_dir)
with ThreadingGroup(*client_hostname) as client_grp:
    client_grp.run(workgen_cmd) # Content saved to lat_{hostname}.log
    client_grp.run(copy_cmd)    # Copy log to /tmp/result in node-0
    