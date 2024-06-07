Two notebooks that show Crossflow being used to create a workflow that links FPocket and AutoDock Vina.

The Jupyter notebook `Pockdock.ipynb` shows a Crossflow workflow that:

1. Downloads a protein-ligand complex from the PDB.
2. Runs FPocket on the protein to find the cavities.
3. Identifies the largest cavity.
4. Prepares the ligand and receptor for docking using AutoDock Tools.
5. Re-docks the ligand into this cavity using AutoDock Vina.
6. Outputs information about the docking, and similarity between docked poses
and the crystal structure conformation.

A second notebook `ReverseDocking.ipynb` extends this to produce a workflow that docks a ligand against a panel of prospective protein partners.
