 [issue-template]: ../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](docs/assets/singnet-logo.jpg 'SingularityNET')


 [![CircleCI](https://circleci.com/gh/Habush/moses-service.svg?style=svg)](https://circleci.com/gh/Habush/mozi_snet_service)    [![Coverage Status](https://coveralls.io/repos/github/Habush/mozi_snet_service/badge.svg?branch=master)](https://coveralls.io/github/Habush/mozi_snet_service?branch=master)      [![BCH compliance](https://bettercodehub.com/edge/badge/Habush/mozi_snet_service?branch=master)](https://bettercodehub.com/)

The [MOSES](https://github.com/opencog/moses) service for SingularityNET


The purpose of this service is to use [MOSES](https://github.com/opencog/moses) for supervised classification of high dimensional data sets with many more features than samples, such as whole genome sequencing data or gene expression data.


#### Running the Service

1. Clone the project:

    ``$ git clone --recursive https://github.com/Habush/moses-service.git``
    
2. Go to the project folder and start docker containers to run the gRPC server and its dependencies (redis, mongo, etc)

    2a. Define the `APP_PORT`, `SERVICE_ADDR` variables. Change `<PORT_NUM>` to the port number you would like to run the result_ui app and `<ADDR>` to the address of the host that you are going to run the app. If you are running this locally, set SERVICE_ADDR to `localhost`



        $ export APP_PORT=<PORT_NUM>
        $ export SERVICE_ADDR=<ADDR>

    2b. Start the docker containers:

        $ docker-compose up

3. Install the python dependencies for running the service client on your local system. Run:

    ``$ pip install grpcio grpcio-tools pyyaml``

4. Generate the gRPC code from the protobufs. Run the following:

    ``$ ./build.sh``
    
    Note: Make sure you have set **execute permission** for `build.sh`. If not, just run `chmod +x build.sh`

5. On a new terminal, while still in the project directory, call the service client. 
    Replace **_<options file>_** with a _.yaml_ file containing the moses and cross-validation **_<dataset file>_** with the path to file you want to run analysis on
    Inputs:
  - `options`: yaml file with MOSES algorithm and cross-validation  parameters.  See [below](#options) for examples.
  - `data`: csv file with observations or samples in rows and binary features in columns labeled **1** for **TRUE** and **0** for **FALSE** for each sample.  The first column should indicate the category label of the sample (**1** for **case** and **0** for **control**).  
 See the doc [here](https://mozi-ai.github.io/moses-service/users_guide/moses-service.html) for a discussion of prepairing specific experimental data types.
    
    ``$ python -m service.moses_service_client <options-file> <dataset-file>``
    
    This will output a link where you can poll the status and download the result files once the analysis is finished.
   
   NOTE: You can find a sample `options.yaml` file in the ``tests/data`` directory of the project

#### Options
```
moses_opts: "-j8 --balance 1 \
  -m 10000 -W1 \
  --output-cscore 1 --result-count 100 \
feature selection parameters
  --enable-fs 1 --fs-algo simple --fs-target-size 4 \
  --fs-focus all --fs-seed init \
# hill climbing parameters
  --hc-widen-search 1 --hc-crossover-min-neighbors 5000 \
  --hc-fraction-of-nn .3 --hc-crossover-pop-size 1000 \
  --reduct-knob-building-effort 1 --complexity-ratio 3"

cross_val_opts:
    folds: 3
    random_seed: 2
    test_size: 0.3

target_feature: "case"
```

#### Calling the Service

You can find details on how to call the service on the github page [here](https://mozi-ai.github.io/moses-service/users_guide/moses-service.html)
