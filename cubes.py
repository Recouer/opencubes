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


def log_if_needed(n, total_n):
    if (n == total_n or n % 100 == 0):
        print(f"\rcompleted {(n / total_n) * 100:.2f}%", end="\n" if n == total_n else "")


def generate_polycubes(n: int, use_cache: bool = False) -> list[np.ndarray]:
    """
    Generates all polycubes of size n

    Generates a list of all possible configurations of n cubes, where all cubes are connected via at least one face.
    Builds each new polycube from the previous set of polycubes n-1.
    Uses an optional cache to save and load polycubes of size n-1 for efficiency.

    Parameters:
    n (int): The size of the polycubes to generate, e.g. all combinations of n=4 cubes.
    use_cahe (bool): whether to use cache files. 

    Returns:
    list(np.array): Returns a list of all polycubes of size n as numpy byte arrays

    """
    if n < 1:
        return []
    elif n == 1:
        return [np.ones((1, 1, 1), dtype=np.byte)]
    elif n == 2:
        return [np.ones((2, 1, 1), dtype=np.byte)]

    if (use_cache and cache_exists(n)):
        results = get_cache(n)
        print(f"\nGot polycubes from cache n={n}")
    else:
        pollycubes = generate_polycubes(n-1, use_cache)

        known_ids = set()
        done = 0
        print(f"\nHashing polycubes n={n}")
        for base_cube in pollycubes:
            for new_cube in expand_cube(base_cube):
                cube_id = get_canonical_packing(new_cube, known_ids)
                known_ids.add(cube_id)
            log_if_needed(done, len(pollycubes))
            done += 1
        log_if_needed(done, len(pollycubes))

        print(f"\nGenerating polycubes from hash n={n}")
        results = []
        done = 0
        for cube_id in known_ids:
            results.append(unpack(cube_id))
            log_if_needed(done, len(known_ids))
            done += 1
        log_if_needed(done, len(known_ids))

    if (use_cache and not cache_exists(n)):
        save_cache(n, results)

    return results


def get_canonical_packing(polycube: np.ndarray, 
                          known_ids: set[bytes]) -> bytes:
    """
    Determines if a polycube has already been seen.

    Considers all possible rotations of a polycube against the existing 
        ones stored in memory. Returns the id if it's found in the set,
        or the maximum id of all rotations if the polycube is new.

    Parameters:
    polycube (np.array): 3D Numpy byte array where 1 values indicate 
        cube positions. Must be of type np.int8
    known_ids (set[bytes]): A set of all known polycube ids

    Returns:
    cube_id (bytes): the id for this cube

    """
    max_id = b'\x00'
    for cube_rotation in all_rotations(polycube):
        this_id = pack(cube_rotation)
        if (this_id in known_ids):
            return this_id
        if (this_id > max_id):
            max_id = this_id
    return max_id



def can_be_sparsified_csr(matrix: np.ndarray):
    size = matrix.shape
    if len(size) > 2:
        size = (size[0], size[1] * size[2])
        return sum(matrix.flatten()) < (size[0] * (size[1] - 1) - 1) / 2

    elif len(size) == 1:
        return sum(matrix.flatten()) < (size[0] * (size[1] - 1) - 1) / 2

    else:
        return False


def can_be_sparsified_coo(matrix: np.ndarray):
    return sum(matrix.flatten()) / len(matrix.flatten()) < 1/3


def return_cube_is_shrunk_coo(matrix: np.ndarray) -> (bool, any):
    if can_be_sparsified_coo(matrix):
        shape = matrix.shape
        if len(shape) > 2:
            matrix = matrix.resize((shape[0], shape[1] * shape[2]))
        return (True, shape), sp.coo_matrix(matrix)
    else:
        return False, matrix


def return_cube_is_shrunk_csr(matrix: np.ndarray) -> ((bool, tuple[int, int, int]), any):
    if can_be_sparsified_csr(matrix):
        shape = matrix.shape
        if len(shape) > 2:
            print(matrix.dtype)
            return (True, shape), sp.csr_matrix(matrix.resize((shape[0], shape[1] * shape[2])))
        return (True, shape), sp.csr_matrix(matrix)
    else:
        return (False, ()), matrix


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Polycube Generator',
        description='Generates all polycubes (combinations of cubes) of size n.')

    parser.add_argument('n', metavar='N', type=int,
                        help='The number of cubes within each polycube')

    # Requires python >=3.9
    parser.add_argument('--cache', action=argparse.BooleanOptionalAction)
    parser.add_argument('--render', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    n = args.n
    use_cache = args.cache if args.cache is not None else True
    render = args.render if args.render is not None else False

    # Start the timer
    t1_start = perf_counter()

    tracemalloc.start()
    all_cubes = generate_polycubes(n, use_cache=use_cache)
    print("simple implementation memory used: ", all_cubes.__sizeof__())
    tracemalloc.stop()

    tracemalloc.start()
    all_cubes_csr = [(return_cube_is_shrunk_csr(cube)) for cube in all_cubes]
    print("csr implementation memory used: ", all_cubes_csr.__sizeof__())
    tracemalloc.stop()

    tracemalloc.start()
    all_cubes_coo = [(return_cube_is_shrunk_coo(cube)) for cube in all_cubes]
    print("coo implementation memory used: ", all_cubes_coo.__sizeof__())
    tracemalloc.stop()

    sparsity = sum([sum(cube.flatten()) / len(cube.flatten()) for cube in all_cubes]) / len(all_cubes)
    print("we have the sparsity : ", sparsity)

    should_be_sparsified_csr = sum([1 if can_be_sparsified_csr(cube) else 0 for cube in all_cubes]) / len(all_cubes)
    should_be_sparsified_coo = sum([1 if can_be_sparsified_coo(cube) else 0 for cube in all_cubes]) / len(all_cubes)
    print(should_be_sparsified_coo, should_be_sparsified_csr)

    # Stop the timer
    t1_stop = perf_counter()

    if (render):
        render_shapes(all_cubes, "./out")

    print(f"\nFound {len(all_cubes)} unique polycubes")
    print(f"\nElapsed time: {round(t1_stop - t1_start,3)}s")
