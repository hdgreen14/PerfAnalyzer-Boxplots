import os
from collections import OrderedDict
import subprocess

"""
A simple script that runs the triton performance analyzer a set number of times for a list of given commands,
and organizes the output csv files by model and batchsize.
"""

commands = OrderedDict()
commands['deepmet'] = "perf_analyzer -m deepmet -u triton-5gb.cms.geddes.rcac.purdue.edu:8001 -i grpc --percentile=95 --async -p 30000 --concurrency-range 4:4 -b 100 --model-repository=/depot/cms/purdue-af/triton/models/ --input-data zero"
#commands['deeptau_nosplit'] = "perf_analyzer -m deeptau_nosplit --percentile=95 -u localhost:8021 -i grpc --async -p 9000 --concurrency-range 4:4 -b"

#define csv headers
fileheaders = "\"Concurrency,Inferences/Second,Client Send,Network+Server Send/Recv,Server Queue,Server Compute Input,Server Compute Infer,Server Compute Output,Client Recv,p50 latency,p90 latency,p95 latency,p99 latency\""


outdir = os.getcwd() + "/output/"
if not os.path.isdir(outdir):
    subprocess.run(f"mkdir {outdir}", shell=True)
for model, command in commands.items(): #adapted from SONIC model optimization script
    outdirmod = f"{outdir}{model}/" #current working directory
    if not os.path.isdir(outdirmod):
        subprocess.run(f"mkdir {outdirmod}", shell=True)
    for batch in [8]: #run perfanalyzer command
        currentfile = f"{outdirmod}{model}_batch{batch}.csv" #working file
        if not os.path.isdir(currentfile):
            subprocess.run(f"touch {currentfile}; echo {fileheaders} {currentfile}", shell=True) #add headers
        tmp = command
        if not os.path.isdir(outdir):
            subprocess.run(f"touch {outdir}tempout.csv", shell=True)
        tmp += f" {batch} -f {outdir}tempout.csv; sed -n '2p' \"{outdir}tempout.csv\" >> \"{currentfile}\" "

        print(tmp)
        for repeat in range(0, 4): #repeat n times
            subprocess.run(f"{tmp}", shell=True) #run command
        