import numpy as np
import mdtraj as mdt

t = mdt.load('1qy1.pdb')
mols = t.topology.find_molecules()
molinds = []
for mol in mols:
    molinds.append([a.index for a in mol])
x_new = t.xyz[0].copy()
for mi in molinds:
    x_tmp = x_new[mi]
    dx = np.random.rand(*x_tmp.shape) - 0.5
    x_tmp += dx * 0.01
    dx = np.random.rand(3) - 0.5
    x_tmp[:] += dx * 0.05
    x_new[mi] = x_tmp
t_new = mdt.Trajectory(x_new, t.topology)
t_new.save('shifted.pdb')    
