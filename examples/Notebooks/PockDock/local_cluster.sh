#!/bin/bash
#
# Start a local dask cluster
dask-scheduler --scheduler-file dask.dat &
sleep 3
dask-worker --scheduler-file dask.dat &
