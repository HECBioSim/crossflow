#!/bin/bash
#
# Example Slurm script to launch a dask cluster consisting of a scheduler
# and twenty  workers, then run a workflow job on it.
#
# This particular HPC system has nodes with 8 Ampere GPUs, each of which
# appears as seven smaller GPUs via Nvidia's multi-instance GPU facility.
# Each worker will have exclusive access to one GPU
#SBATCH --mem=200g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=20
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:20
#SBATCH -p ampere-mq
#SBATCH --time=04:00:00
#SBATCH -J example

# Launch the scheduler
dask-scheduler --scheduler-file scheduler.json &
# after a short pause, launch the workers
sleep 5
srun dask-mig-worker &
# Run the crossflow workflow, which will connect to the cluster
# via the information written by the scheduler to the file scheduler.json
python workflow.py
echo 'all done'
