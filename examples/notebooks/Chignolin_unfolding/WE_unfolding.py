#!/usr/bin/env python
# coding: utf-8

# Demonstration Weighted Ensemble Simulation - Chignolin unfolding
#
# This notebook illustrates how you can write a simple Weighted Ensemble simulation workflow using crossflow.
#
# It is assumed that you already have a Dask Distributed cluster up and running - see the ./cluster folder for a recipie to do this on a Condor cluster. Each Dask worker should be on its own GPU node.
#
# The input files are taken from the WESTPA tutorial.
#
# -----
#
# Import required packages:
#

import logging
import time

import mdtraj as mdt
import numpy as np

from crossflow.clients import Client
from crossflow.filehandling import FileHandler
from crossflow.kernels import SubprocessKernel

logging.basicConfig(filename="we_unfolding.log", level=logging.DEBUG)
# Convert the starting structure into an Amber .ncrst format file via MDTraj:

ref = mdt.load("common_files/chignolin.pdb")
ref.save("chignolin.ncrst")

# Load the required starting files:

fh = FileHandler()
mdin = fh.load("common_files/md.in")
crds = fh.load("chignolin.ncrst")
prmtop = fh.load("common_files/chignolin.prmtop")

# Create a SubprocessKernel that runs pmemd. All we need back are the
# final coordinates.

pmemd = SubprocessKernel(
    "pmemd.cuda -i mdin -c x.inpcrd -p x.prmtop -r x.ncrst -o x.log"
)
# pmemd = SubprocessKernel('mpirun pmemd.MPI -i mdin -c x.inpcrd -p x.prmtop -r x.ncrst -o x.log')
pmemd.set_inputs(["mdin", "x.inpcrd", "x.prmtop"])
pmemd.set_outputs(["x.ncrst"])
pmemd.set_constant("mdin", mdin)
pmemd.set_constant("x.prmtop", prmtop)


# Create a crossflow client that talks to our dask cluster:

client = Client(scheduler_file="cluster/scheduler.json")

# We will have a target of 4 simulations per WE bin, and the bins are defined
# by RMSD from the starting structure, between 0.05 nm (limit of what is
# considered 'native' structure) and 0.40 nm (above which is 'unfolded'
# target state), in 0.02 nm increments. We will run the WE simulation for 50
# cycles.

n_cycles = 1000
n_reps = 4
bin_edges = np.arange(0.05, 0.42, 0.02)
target_bin = len(bin_edges)


# Here is the workflow:

# Begin with n_rep copies of the starting structure, with equal weights:
starting_coordinates = [crds] * n_reps
weights = [1.0 / n_reps] * n_reps
# Record what gets recycled each cycle:
recycled_flux = []
# Run a simularton step on each:
start = time.time()
restarts = client.map(pmemd, starting_coordinates)
# Main loop:
for c in range(n_cycles):
    # Calculate which bin each restart structure falls in to:
    t = mdt.load([str(r.result()) for r in restarts], top=str(prmtop))
    bin_ids = np.digitize(mdt.rmsd(t, ref), bin_edges)
    # Calculate the weight which has reached the final target bin:
    recycled_weight = np.where(bin_ids == target_bin, weights, 0.0).sum()
    logging.info("Cycle {}: recycled weight={}".format(c, recycled_weight))
    recycled_flux.append(recycled_weight)
    # Recycle any simulations that have reached the target state back to
    # the starting state:
    restarts = np.where(bin_ids == target_bin, crds, restarts)
    bin_ids = np.where(bin_ids == target_bin, 0, bin_ids)
    # Assign restart structures to bins and calculate the total weight in
    # each bin:
    bins = {}
    bin_wts = {}
    for i, r in enumerate(restarts):
        if bin_ids[i] in bins:
            bins[bin_ids[i]].append(r)
            bin_wts[bin_ids[i]] += weights[i]
        else:
            bins[bin_ids[i]] = [r]
            bin_wts[bin_ids[i]] = weights[i]
    # Report various metrics
    n_occ = len(set(bin_ids))
    bin_wt_min = min(bin_wts.values())
    bin_wt_max = max(bin_wts.values())
    walker_wt_min = min(weights)
    walker_wt_max = max(weights)
    now = time.time()
    cycle_time = now - start
    logging.info("{} walkers in total".format(len(restarts)))
    logging.info("{} of {} bins are populated".format(n_occ, target_bin))
    logging.info("per-bin minimum non-zero probability: {:8.6f}".format(bin_wt_min))
    logging.info("per-bin maximum probability: {:8.6f}".format(bin_wt_max))
    logging.info(
        "per-walker minimum non-zero probability: {:8.6f}".format(walker_wt_min)
    )
    logging.info("per-walker maximum probability: {:8.6f}".format(walker_wt_max))
    logging.info("Time for this cycle: {:8.1f}s".format(cycle_time))
    start = now
    # Replicate or cull simulations from each bin to leave n_reps in each,
    # then reallocate the total bin weight evenly amongst the structures:
    starting_coordinates = []
    weights = []
    for bin in bins:
        starting_coordinates += list(np.random.choice(bins[bin], n_reps))
        weights += [bin_wts[bin] / n_reps] * n_reps
    # Run the next round of simulations:
    restarts = client.map(pmemd, starting_coordinates)

recycled_flux = np.array(recycled_flux) / 20  # flux per picosecond
np.save("recycled_flux.npy", recycled_flux)
