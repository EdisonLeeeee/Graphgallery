import numpy as np
import scipy.sparse as sp

from ..transforms import BaseTransform
from .to_edge import sparse_adj_to_edge
from ..get_transform import Transform


@Transform.register()
class SparseReshape(BaseTransform):
    """Add self loops for adjacency matrix."""

    def __init__(self, shape: tuple = None):
        """
        Parameters
        ----------
            shape: new shape.
        """
        super().__init__()
        self.shape = shape

    def __call__(self, *adj_matrix: sp.csr_matrix) -> sp.csr_matrix:
        """
        Parameters
        ----------
        adj_matrix: Scipy matrix or Numpy array or a list of them 
            Single or a list of Scipy sparse matrices or Numpy arrays.

        Returns
        -------
        Single or a list of Scipy sparse matrix or Numpy matrices.

        See also
        ----------
        graphgallery.functional.sparse_reshape
        """
        return sparse_reshape(*adj_matrix, shape=self.shape)

    def extra_repr(self):
        return f"shape={self.shape}"


def sparse_reshape(adj_matrix: sp.csr_matrix, shape: tuple = None) -> sp.csr_matrix:
    """

    Parameters
    ----------
        adj_matrix: Scipy matrix or Numpy array or a list of them 
            Single or a list of Scipy sparse matrices or Numpy arrays.
        shape: new shape.

    Returns
    -------
        Single or a list of Scipy sparse matrix or Numpy matrices.

    See also
    ----------
        graphgallery.functional.SparseReshape          

    """
    if shape is None:
        return adj_matrix.copy()
    else:
        M1, N1 = shape
        M2, N2 = adj_matrix.shape
        assert (M1 >= M2) and (N1 >= N2)
        edge_index, edge_weight = sparse_adj_to_edge(adj_matrix)
        return sp.csr_matrix((edge_weight, edge_index), shape=shape)
