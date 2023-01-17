import numpy as np

from pyscf.pbc import gto as pbcgto
from pyscf.pbc import tools as pbctools
import pyscf.pbc.tools.pyscf_ase as pyscf_ase

def build_cell(ase_atom, unit='B', ke=20.0, gsmax=None, basis='gth-szv',
               pseudo='gth-pade', dimension=3, incore_anyway=False):
    cell = pbcgto.Cell()
    cell.unit = unit
    cell.atom = pyscf_ase.ase_atoms_to_pyscf(ase_atom)
    cell.a = ase_atom.cell.T

    cell.basis = basis
    cell.pseudo = pseudo
    cell.dimension = dimension

    cell.incore_anyway = incore_anyway

    if gsmax is not None:
        cell.gs = np.array([gsmax, gsmax, gsmax])
    else:
        cell.ke_cutoff = ke

    cell.build(verbose=7)
    return cell
