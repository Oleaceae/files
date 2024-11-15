import os
import re


baseDir = "/Users/Oleaceae/Documents/Work/RTS/archive/2024-11-15@02-28-18"

for fname, outfname in [("log_home-timeline-service.log", "result_home.jtl"), ("log_post-storage-service.log", "result_post.jtl")]:
    with open(os.path.join(baseDir, fname), "r") as f, open(os.path.join(baseDir, outfname), "w") as g:
        lines = f.readlines()
        for line in lines:
            nums = re.findall(r'\d+', line)
            ed = int(nums[-1])
            st = int(nums[-2])
            lat = ed - st

            req_type = line.split(" ")[4]
            g.write(f"{ed} {lat} {req_type}\n")