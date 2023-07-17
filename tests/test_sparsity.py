import numpy as np
import argparse
from time import perf_counter
from libraries.cache import get_cache, save_cache, cache_exists
from libraries.resizing import expand_cube
from libraries.packing import pack, unpack
from libraries.renderer import render_shapes
from libraries.rotation import all_rotations
import tracemalloc
import scipy.sparse as sp
from cubes import generate_polycubes
from sys import getsizeof

def get_sparse_data(sparse_matrix):
    return sparse_matrix.data.nbytes + sparse_matrix.indptr.nbytes + sparse_matrix.indices.nbytes


def can_be_sparsified_csr(matrix: np.ndarray):
    return True
    size = matrix.shape
    if len(size) > 2:
        return matrix.__sizeof__() > sp.csr_array(matrix.reshape(size[0], size[1] *  size[2])).__sizeof__()

    else:
        return matrix.__sizeof__() > sp.csr_array(matrix).__sizeof__()


def can_be_sparsified_coo(matrix: np.ndarray):
    return True
    size = matrix.shape
    if len(size) > 2:
        return matrix.__sizeof__() > sp.coo_array(matrix.reshape(size[0], size[1] *  size[2])).__sizeof__()

    else:
        return matrix.__sizeof__() > sp.coo_array(matrix).__sizeof__()


def return_cube_is_shrunk_coo(matrix: np.ndarray) -> any:
    if can_be_sparsified_coo(matrix):
        shape = matrix.shape
        if len(shape) > 2:
            matrix = matrix.resize((shape[0], shape[1] * shape[2]))
        return sp.coo_matrix(matrix)
    else:
        return matrix


def return_cube_is_shrunk_csr(matrix: np.ndarray) -> any:
    if can_be_sparsified_csr(matrix):
        shape = matrix.shape
        if len(shape) > 2:
            return sp.csr_matrix(matrix.resize((shape[0], shape[1] * shape[2])))
        return sp.csr_matrix(matrix)
    else:
        return matrix




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog='Test sparsity',
    description='look for the sparsity of the polycube implementation and compare it to an implementation with sparse matrices')

    parser.add_argument('n', metavar='N', type=int,
                        help='The max number of cubes within each polycube for the comparison, must be > 5')

    # Requires python >=3.9
    parser.add_argument('--cache', action=argparse.BooleanOptionalAction)
    parser.add_argument('--render', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    n = args.n
    use_cache = args.cache if args.cache is not None else True
    render = args.render if args.render is not None else False


    data = dict()

    
    tracemalloc.start()


    all_cubes = generate_polycubes(n, use_cache=use_cache)

    print(tracemalloc.get_traced_memory())

    all_cubes_csr = [(return_cube_is_shrunk_csr(cube)) for cube in all_cubes]

    print(tracemalloc.get_traced_memory())

    all_cubes_coo = [(return_cube_is_shrunk_coo(cube)) for cube in all_cubes]

    print(tracemalloc.get_traced_memory())

    tracemalloc.stop()


    for i in range(5, 5):
        data[i] = dict()

        all_cubes = generate_polycubes(i, use_cache=use_cache)
        size = sum([cube.__sizeof__() for cube in  all_cubes])
        data[i]["size_current"] = all_cubes.__sizeof__() + size

        all_cubes_csr = [(return_cube_is_shrunk_csr(cube)) for cube in all_cubes]
        size = sum([cube.__sizeof__() for cube in  all_cubes_csr]) 
        data[i]["size_csr"] = all_cubes_csr.__sizeof__() + size

        all_cubes_coo = [(return_cube_is_shrunk_coo(cube)) for cube in all_cubes]
        size = sum([cube.__sizeof__() for cube in  all_cubes_coo]) 
        data[i]["size_coo"] = all_cubes_coo.__sizeof__() + size

        sparsity = sum([sum(cube.flatten()) / len(cube.flatten()) for cube in all_cubes]) / len(all_cubes)
        data[i]["sparsity"] = sparsity

        should_be_sparsified_csr = sum([1 if can_be_sparsified_csr(cube) else 0 for cube in all_cubes]) / len(all_cubes)
        should_be_sparsified_coo = sum([1 if can_be_sparsified_coo(cube) else 0 for cube in all_cubes]) / len(all_cubes)
        data[i]["sparsified_csr"] = should_be_sparsified_csr
        data[i]["sparsified_coo"] = should_be_sparsified_coo

    print(data)

