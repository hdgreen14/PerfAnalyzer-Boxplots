## Setup

To run the NVIDIA performance analyzer, you first must download the triton client package from docker. Use the below command in apptainer:

```apptainer build tritoncli.sif docker:nvcr.io/nvidia/tritonserver:21.10-py3-sdk```

After downloading this package, you only need to run the below command to launch the image on subsequent startups.

```singularity run ./tritoncli.sif```


## Using Triton Performance Analyzer
See the below link for more detailed information:

[Perf Analyzer CLI](https://github.com/triton-inference-server/client/blob/main/src/c%2B%2B/perf_analyzer/docs/cli.md#measurement-options)

A good example of a command to put in the boxplot script is below:


'''perf_analyzer -m [model (ex, deepmet)] -u [ip address:port number] -i grpc --percentile=95 --async -p 60000 --concurrency-range 4:4 -b 100 --model-repository=[model directory (ex, /home/user/models/)] --input-data "zero" -f [outputfile].csv'''

Other examples can be found in the script itself. 



## Using the Script

If a /outputs/ folder already exists, put the script in it's root directory. Run the script inside the triton image. Boxplots will be saved in the same directory as the script by default.
