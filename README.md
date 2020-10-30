# Computational Intelligence for the Humanities Servers

## Basic initial setup

On a newly-provisioned AWS instance, bootstrap this code base by installing Git and cloning this repository, and the starcoder-experiments repository:

```
sudo yum install git
git clone -b dev git@github.com:starcoder/cih-servers.git
git clone -b dev git@github.com:starcoder/starcoder-experiments.git
cd cih-servers
```

The rest of the software can then be installed and configured by running a script with a single argument, a fully-qualified domain name of the computer (probably the URL people will enter to browse to it), e.g.:

```
scripts/provision_aws.sh ec2-107-23-90-233.compute-1.amazonaws.com
```

Note that this script removes and reinstalls almost everything from scratch, so make sure this is what you want to happen.  For fine-grained control, and to understand how the servers are arranged, the script is well-documented.

When complete (should be <10 minutes), three servers will be running: PostGRESQL, ElasticSearch, and Kibana, on ports 5432, 9200, and 5601 respectively.  You will also be in a position to start the primary CIH server (if your starcoder-experiments repository wasn't cloned as described above, you should set `STARCODER_EXPERIMENTS_PATH` correctly in the file `primary_server/settings.py`).  You will also probably want to run something like:

```
cp ../starcoder-experiments/custom.py.example ../starcoder-experiments/custom.py
```

and then edit the `../starcoder-experiments/custom.py` file to define (or uncomment) some experiments, and perhaps *run* the experiments, so there's something interesting to load into the server.

## General workflow

At this point, you can start working on filling the databases with interesting research.