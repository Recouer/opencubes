from __future__ import annotations
import sys
from time import perf_counter
import numpy as np
from holder import PolycubeHolder
from polycube import PolyCube
from utils import identity_to_tag, render_shapes
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
        initial_holder = PolycubeHolder("C0")
        initial_holder.add_polycube(PolyCube(np.array([[0]]), [(0, 0, 0)]))

        self.polycube_per_number_of_cubes: dict[int, dict[str, PolycubeHolder]] = \
            {1: {"C0": initial_holder}}

    def render_shapes(self, output_file: str, number_of_cubes: int = 0, shapes: str = ""):
        polycubes = []
        if number_of_cubes == 0:
            if shapes == "":
                for _, by_number in self.polycube_per_number_of_cubes.items():
                    for _, by_shape in by_number.items():
                        polycubes += by_shape.polycubes
        elif shapes == "":
            for _, by_shape in self.polycube_per_number_of_cubes[number_of_cubes].items():
                polycubes += by_shape.polycubes

        else:
            polycubes += self.polycube_per_number_of_cubes[number_of_cubes][shapes].polycubes

        polycubes = [polycube.get_3D_representation() for polycube in polycubes]
        print(polycubes)

        render_shapes(polycubes, output_file)

    def solve(self, cube_number: int):
        for i in range(1, cube_number):
            print(i)
            self.polycube_per_number_of_cubes[i + 1] = dict()
            for polycube_type in self.polycube_per_number_of_cubes[i]:
                for polycube in self.polycube_per_number_of_cubes[i].get(polycube_type).polycubes:
                    new_PCPOs = polycube.iterate_through_All_PCPO()
                    for PCPO in new_PCPOs:
                        tag = identity_to_tag(PCPO.cube_identity)
                        if self.polycube_per_number_of_cubes[i + 1].get(tag) is not None:
                            self.polycube_per_number_of_cubes[i + 1][tag].add_polycube(PCPO)
                        else:
                            self.polycube_per_number_of_cubes[i + 1][tag] = PolycubeHolder(tag)
                            self.polycube_per_number_of_cubes[i + 1][tag].add_polycube(PCPO)


if __name__ == "__main__":
    # Start the timer
    tracemalloc.start()
    t1_start = perf_counter()

    solver = CubeSolver()
    solver.solve(4)
    solver.render_shapes("out", 4)
    print(solver)

    # Stop the timer
    t1_stop = perf_counter()

    print(f"Elapsed time: {round(t1_stop - t1_start, 3)}s")
    print(tracemalloc.get_traced_memory())

    # val = np.load("../tests/cubes_7.npy", allow_pickle=True)
    # print(len(val))
    tracemalloc.stop()
    # print(val)

    # 8: (28455485, 30759926) ~ 30M -> ~12000 elements
    # 7: (4279135, 4587013) ~ 4.5M -> ~2000 elements
