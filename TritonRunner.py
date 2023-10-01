import os
import glob
import re
import csv
from collections import OrderedDict
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

def getValue(filename: str, yPara, linename):
    """
    Inputs: filename, paramater to search for
    Output: List of values that match header asked for in yPara as a dictionary in form filename : [values of row]
    """

    valuedict = {}
    yval = np.array([])

    data_dict = {}

    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #can't skip if a file onlly has headers - fix that
        keys = next(csv_reader)   
        columns = [[] for i in range(len(keys))] 
        for row in csv_reader:
            for i, value in enumerate(row):
                if re.search( r'^\d+(\.\d+)?$', value): #ignore header
                    columns[i].append(value)
        
        data_dict = {keys[i]: columns[i] for i in range(len(keys))}

        if yPara in data_dict.keys():
            value =  np.fromiter(data_dict[yPara], dtype=float)
            if (yPara != "Concurrency") and (yPara != "Client Recv"):
                value = np.divide(value, 1000)
                yval = np.append(yval, values= value)
            else:
                yval = np.append(yval, values = value)
        valuedict[linename] = yval
        return valuedict.values()
    



commands = {}
commands['deepmet'] = "perf_analyzer -m deepmet -u triton-5gb.cms.geddes.rcac.purdue.edu:8001 -i grpc --percentile=95 --async -p 10000 --concurrency-range 4:4 -b 100 --model-repository=/depot/cms/purdue-af/triton/models/ --input-data zero"
#commands['particlenet'] = "perf_analyzer -m particlenet -u triton-5gb.cms.geddes.rcac.purdue.edu:8001 -i grpc --percentile=95 --async -p 10000 --concurrency-range 4:4 -b 100 --model-repository=/depot/cms/purdue-af/triton/models/ --input-data zero"

#commands['deeptau_nosplit'] = "perf_analyzer -m deeptau_nosplit --percentile=95 -u localhost:8021 -i grpc --async -p 9000 --concurrency-range 4:4 -b"
graphTitles = {}
for model in commands.keys():
    graphTitles[model] = {} #in form {model : {batch : {boxname : values} , .. ,  } }

#singularity run /depot/cms/users/green642/tritoncli.sif
outdir = os.getcwd() + "/output/"
if not os.path.isdir(outdir):
    subprocess.run(f"mkdir {outdir}", shell=True)
for model, command in commands.items(): #adapted from SONIC model optimization script
    outdirmod = f"{outdir}{model}/" #current working directory
    if not os.path.isdir(outdirmod):
        subprocess.run(f"mkdir {outdirmod}", shell=True)
    for batch in [8, 16, 32]: #run perfanalyzer command
        currentfile = f"{outdirmod}{model}_batch{batch}.csv" #working file
        if not os.path.isdir(currentfile):
            subprocess.run(f"touch {currentfile}; echo \"Concurrency,Inferences/Second,Client Send,Network+Server Send/Recv,Server Queue,Server Compute Input,Server Compute Infer,Server Compute Output,Client Recv,p50 latency,p90 latency,p95 latency,p99 latency\" {currentfile}", shell=True) #headers
        tmp = command
        if not os.path.isdir(outdir):
            subprocess.run(f"touch {outdir}tempout.csv", shell=True)
        tmp += f" {batch} -f {outdir}tempout.csv; sed -n '2p' \"{outdir}tempout.csv\" >> \"{currentfile}\" "

        for repeat in range(0, 3):
            subprocess.run(f"{tmp}", shell=True) #run command
        #print(getValue(currentfile, "Inferences/Second", f"{model}, Batchsize: {batch}"))
        graphTitles[model][batch] = getValue(currentfile, "Inferences/Second", f"{model}, Batchsize: {batch}")



#make plot
finaldict= {}
for model, batchsize in graphTitles.items():
    print("\nmodel", model)
    
    for key in batchsize:
        finaldict[f'{model}, {key}:']= list(graphTitles[model][key])
        
    arr = [] #flatten
    for i in finaldict.values():
        arr.append(np.ravel(i))
    plt.boxplot(arr, labels= finaldict.keys(), vert=False)    
    plt.tight_layout()
    plt.savefig(f"{model}_{batchsize}.png")
    plt.show()



subprocess.run(f"rm {outdir}tempout.csv", shell=True)
