#!/bin/bash
#
# Start a local dask cluster
dask-scheduler --pid-file scheduler.pid --scheduler-file dask.dat &
sleep 3
dask-worker --scheduler-file dask.dat --nworkers auto --resources 'tasks=1'&
