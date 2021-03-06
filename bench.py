import time

import numpy as np
import scipy.sparse as sp
from numpy.testing import assert_array_almost_equal

from dotbench import sparse_dense
from dotbench import sparse_sparse_binary_search
from dotbench import sparse_sparse_hash_map
from dotbench import sparse_sparse_incremental

def gen_sparse_matrix(shape, sparsity):
    """Efficient generation of random sparse matrix"""
    n_samples, n_features = shape
    n_nz = int(n_features * sparsity) # number of non-zero elements per sample
    data = np.random.random(n_samples * n_nz)
    row_ind = np.arange(n_samples)
    col_ind = np.arange(n_features)
    row = np.repeat(row_ind, n_nz)
    col = np.zeros(n_samples * n_nz)
    for i in range(n_samples):
        np.random.shuffle(col_ind)
        start = i * n_nz
        end = start + n_nz
        col[start:end] = col_ind[:n_nz]
    return sp.coo_matrix((data, (row,col)), shape=shape).tocsr()

def sparsity(arr):
    return len(arr.data) * 1.0 / (arr.shape[0] * arr.shape[1])

def timeit(func, *args):
    start = time.time()
    func(*args)
    return time.time() - start

if __name__ == '__main__':
    import sys

    # parse command line options
    opt = {}
    for i, o in enumerate([("n_samples", 1000, int),
                           ("n_features", 10000, int),
                           ("matrix_sparsity", 0.1, float),
                           ("weight_sparsity", 0.7, float)]):
        o_name, o_dflt, o_type= o
        try:
            opt[o_name] = o_type(sys.argv[i+1])
        except:
            opt[o_name] = o_dflt

    # generate data
    shape = (opt["n_samples"], opt["n_features"])
    print "Loading matrix..."
    print "Shape: ", shape
    print "Sparsity: ", opt["matrix_sparsity"]
    X = gen_sparse_matrix(shape,
                          opt["matrix_sparsity"])
    print "Loading vector..."
    shape = (1, opt["n_features"])
    print "Shape: ", shape
    print "Sparsity: ", opt["weight_sparsity"]
    w = gen_sparse_matrix(shape,
                          opt["weight_sparsity"])

    print "Sorting indices..."
    X.sort_indices()
    w.sort_indices()

    print "sparse-dense"
    out_ref = np.zeros(X.shape[0], dtype=np.float64)
    print timeit(sparse_dense, X, w.toarray().ravel(), out_ref)

    print "sparse-sparse binary search"
    out = np.zeros(X.shape[0], dtype=np.float64)
    print timeit(sparse_sparse_binary_search, X, w, out)
    assert_array_almost_equal(out, out_ref)

    print "sparse-sparse hash map"
    out = np.zeros(X.shape[0], dtype=np.float64)
    print timeit(sparse_sparse_hash_map, X, w, out)
    assert_array_almost_equal(out, out_ref)

    print "sparse-sparse incremental"
    out = np.zeros(X.shape[0], dtype=np.float64)
    print timeit(sparse_sparse_incremental, X, w, out)
    assert_array_almost_equal(out, out_ref)

