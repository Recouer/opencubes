from __future__ import annotations

from time import perf_counter

import numpy as np
import cube_utils as cu
import tracemalloc

class CubeSolver:
    def __repr__(self):
        value = []
        for i in self.polycube_per_number_of_cubes.keys():
            value.append(0)
            for format in self.polycube_per_number_of_cubes[i].keys():
                value[-1] += self.polycube_per_number_of_cubes[i][format].number_of_polycubes()
        string = self.polycube_per_number_of_cubes.__repr__() + value.__repr__()
        return string

    def __init__(self):
        initial_holder = cu.PolycubeHolder("C0")
        initial_holder.add_polycube(cu.PolyCube(np.array([[0]]), [(0, 0, 0)]))

        self.polycube_per_number_of_cubes = {1: {"C0": initial_holder}}

    def solve(self, cube_number: int):
        for i in range(1, cube_number):
            print(i)
            self.polycube_per_number_of_cubes[i + 1] = dict()
            for polycube_type in self.polycube_per_number_of_cubes[i]:
                for polycube in self.polycube_per_number_of_cubes[i].get(polycube_type).polycubes:
                    new_PCPOs = polycube.iterate_through_All_PCPO()
                    for PCPO in new_PCPOs:
                        tag = cu.identity_to_tag(PCPO.cube_identity)
                        if self.polycube_per_number_of_cubes[i + 1].get(tag) is not None:
                            self.polycube_per_number_of_cubes[i + 1][tag].add_polycube(PCPO)
                        else:
                            self.polycube_per_number_of_cubes[i + 1][tag] = cu.PolycubeHolder(tag)
                            self.polycube_per_number_of_cubes[i + 1][tag].add_polycube(PCPO)


if __name__ == "__main__":
    # Start the timer
    tracemalloc.start()
    t1_start = perf_counter()

    solver = CubeSolver()
    solver.solve(7)
    print(solver)

    # Stop the timer
    t1_stop = perf_counter()

    print(f"Elapsed time: {round(t1_stop - t1_start, 3)}s")
    print(tracemalloc.get_traced_memory())

    val = np.load("../cubes_7.npy", allow_pickle=True)
    print(len(val))
    tracemalloc.stop()
    # print(val)

    # 8: (28455485, 30759926) ~ 30M -> ~12000 elements
    # 7: (4279135, 4587013) ~ 4.5M -> ~2000 elements
