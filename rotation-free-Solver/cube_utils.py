from __future__ import annotations
import copy
import os
import sys
import math
import numpy as np
import argparse
from time import perf_counter
import geometry_utils as gu
import types
import numpy.typing as npt
from collections import Counter


def has_equivalence(connection: int, _parse: int, eq_list: dict):
    if _parse in eq_list.values() and (eq_list[connection] != _parse):
        return False

    if eq_list[connection] == 0:
        eq_list[connection] = _parse
        eq_list[gu.get_opposite(connection)] = gu.get_opposite(_parse)
        return True

    return eq_list[connection] == _parse


def identity_to_tag(identity: npt.NDArray):
    tag = ""
    values = dict(Counter(identity))

    for connectivity in range(7):
        occurrences = values.get(connectivity)
        if occurrences is not None:
            if connectivity == 0:
                tag = "C0"
            elif connectivity == 1:
                tag += f"H{occurrences}"
            else:
                tag += f"_{occurrences}C{connectivity}"

    return tag


def update_adjacency_matrix(adjacency_matrix, position_vector):
    size = len(position_vector)
    adjacent_position = [
        tuple(np.array(position_vector)[-1] + np.array((0, 1, 0))),
        tuple(np.array(position_vector)[-1] + np.array((0, -1, 0))),
        tuple(np.array(position_vector)[-1] + np.array((1, 0, 0))),
        tuple(np.array(position_vector)[-1] + np.array((-1, 0, 0))),
        tuple(np.array(position_vector)[-1] + np.array((0, 0, 1))),
        tuple(np.array(position_vector)[-1] + np.array((0, 0, -1)))
    ]

    for i, cube in enumerate(position_vector):
        if i == len(position_vector) - 1:
            pass

        if tuple(cube) in adjacent_position:
            adj = gu.get_adjacency_from_positions(cube, position_vector[-1])
            adjacency_matrix[i, size - 1] = gu.get_opposite(adj)
            adjacency_matrix[size - 1, i] = adj


class PolyCube:
    def __init__(self, adjacency_matrix: npt.NDArray, position_vector: list):
        self.adjacency_matrix = adjacency_matrix
        self.position_vector = position_vector
        self.size = np.shape(adjacency_matrix)[0]
        self.__parses = []

        neighbor_list = []
        for cube in self.adjacency_matrix:
            neighbor_list += [gu.get_number_of_neighbors(np.sum(cube))]
        self.cube_identity = np.array(neighbor_list)

    def __repr__(self):
        # string = self.cube_identity.__repr__() + "\n"
        string = self.position_vector.__repr__() + "\n"
        # string += self.adjacency_matrix.__repr__() + "\n"
        return string

    def get_parses(self, starter_nodes: int):
        if self.__parses:
            returned_parses = copy.deepcopy(self.__parses)
            return returned_parses

        indexes = [index for index in range(len(self.cube_identity)) if self.cube_identity[index] == starter_nodes]
        if not indexes:
            raise AttributeError("starter node not present into the polycube")

        sort_order = [2, 16, 1, 8, 4, 32]

        def create_parse_rec(adjacency_matrix: npt.NDArray,
                             parse_list: list[int],
                             node: int,
                             traversed_node: list[bool]):
            traversed_node[node] = True
            adjacency_list = dict(
                [(adjacency, i) for (i, adjacency) in enumerate(adjacency_matrix[node]) if adjacency != 0]
            )
            for adjacency in sort_order:
                if adjacency in adjacency_list.keys() and not traversed_node[adjacency_list[adjacency]]:
                    parse_list += [adjacency]
                    create_parse_rec(adjacency_matrix, parse_list, adjacency_list[adjacency], traversed_node)

        for index in indexes:
            parse_list = []
            create_parse_rec(self.adjacency_matrix, parse_list, index,
                             [False for _ in range(len(self.adjacency_matrix))])
            if parse_list not in self.__parses:
                self.__parses += [copy.deepcopy(parse_list)]

        returned_parses = copy.deepcopy(self.__parses)
        return returned_parses

    def create_PCPO(self):
        return np.pad(self.adjacency_matrix, (1, 1))[1:, 1:]

    def iterate_through_All_PCPO(self):
        for i in range(self.size):
            available_space = 63 - np.sum(self.adjacency_matrix[i])
            for position in gu.iterate_through(available_space):
                new_adjacency_matrix = self.create_PCPO()
                new_adjacency_matrix[i, self.size] = position
                new_adjacency_matrix[self.size, i] = gu.get_opposite(position)

                new_position_vector = copy.deepcopy(self.position_vector)
                new_position_vector += gu.get_position_from_adjacency(self.position_vector[i], position)

                update_adjacency_matrix(new_adjacency_matrix, new_position_vector)

                yield PolyCube(new_adjacency_matrix, new_position_vector)


class Sorter:
    def __init__(self):
        self.children: dict[int, Sorter] = dict()
        self.leaf_polycube = None

    def __repr__(self):
        if self.leaf_polycube is not None:
            string = self.leaf_polycube.__repr__()
        else:
            string = self.children.__repr__()
        return string

    def add_get_child(self, position: int) -> Sorter:
        child = self.children.get(position)
        if child is None:
            child = Sorter()
            self.children[position] = child

        return child

    def add_polycube(self, polycube: PolyCube, polyparse: list[int], eq_dict: dict[int, int]) -> bool:
        child = self
        for _parse in polyparse:
            polycube_parse = eq_dict[_parse] if eq_dict[_parse] != 0 else _parse
            child = child.add_get_child(polycube_parse)
        if child.leaf_polycube is None:
            child.leaf_polycube = polycube
            return True
        return False


class PolycubeSorter:
    def __init__(self):
        self.sorter: Sorter = Sorter()
        self.starter_node: int = -1

    def __repr__(self):
        string = f"starter node: {self.starter_node}\n"
        string += self.sorter.__repr__()
        return string

    def is_inside_rec(self, sorter: Sorter, poly_parse: list[int], eq_list: dict[int, int]) -> bool:
        if len(poly_parse) > 0:
            connection = poly_parse.pop(0)
            return_value = False
            for (child, child_sorter) in sorter.children.items():
                new_list = copy.deepcopy(eq_list)
                if has_equivalence(connection, child, new_list):
                    return_value |= self.is_inside_rec(child_sorter, copy.deepcopy(poly_parse), new_list)
            return return_value
        else:
            return True

    def try_add_polycube(self, polycube: PolyCube) -> bool:

        if self.starter_node < 0:
            counter = Counter(polycube.cube_identity)
            # here the starter node is represented by the amount of connections it has
            self.starter_node = min(counter, key=counter.get)

            polycube_parses = [parses for parses in polycube.get_parses(self.starter_node)]
            sorter = self.sorter
            for _parse in polycube_parses[0]:
                sorter = sorter.add_get_child(_parse)
            sorter.leaf_polycube = polycube

            return True

        else:
            polycube_parsers = polycube.get_parses(self.starter_node)
            can_be_added = True
            equivalence_list = dict({1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0})
            final_eq_list: dict[any, int] = dict({1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0, "index": -1})
            for polycube_parse in polycube_parsers:
                final_eq_list["index"] = final_eq_list["index"] + 1
                if self.is_inside_rec(self.sorter, polycube_parse, equivalence_list):
                    can_be_added = False

            if can_be_added:
                polyparses = polycube.get_parses(self.starter_node)
                self.sorter.add_polycube(polycube, polyparses[final_eq_list["index"]], final_eq_list)
                return True
            return False


class PolycubeHolder:
    def __init__(self, polycube_tag: str):
        self.polycube_tags = polycube_tag
        self.sorter = PolycubeSorter()
        self.polycubes = []

    def __repr__(self):
        string = "\n" + self.polycubes.__repr__() + "\n"
        # string += self.sorter.__repr__() + "\n"
        # string = f"{len(self.polycubes)}"
        return string

    def number_of_polycubes(self):
        return len(self.polycubes)

    def add_polycube(self, polycube: PolyCube):
        if identity_to_tag(polycube.cube_identity) == self.polycube_tags:
            if self.sorter.try_add_polycube(polycube):
                self.polycubes.append(polycube)


# region UnitTest

def test_has_equivalence():
    eq_list = {1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0}

    assert has_equivalence(1, 2, eq_list)
    assert eq_list[1] == 2
    assert eq_list[8] == 16
    assert has_equivalence(8, 16, eq_list)

    assert has_equivalence(2, 4, eq_list)
    assert eq_list[2] == 4
    assert eq_list[16] == 32
    assert has_equivalence(16, 32, eq_list)


def test_PolycubeSorter_try_add_polycube():
    poly1 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (-1, 0, 0), (-1, 1, 0)]),
        [(0, 0, 0), (-1, 0, 0), (-1, 1, 0)]
    )
    poly3 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (-1, 0, 0), (0, 1, 0)]),
        [(0, 0, 0), (-1, 0, 0), (0, 1, 0)]
    )
    poly2 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (0, 2, 0)]),
        [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
    )
    sorter = PolycubeSorter()

    print(poly1.get_parses(2))
    print(poly3.get_parses(2))

    assert sorter.try_add_polycube(poly1)
    assert sorter.try_add_polycube(poly3) == False
    assert sorter.try_add_polycube(poly2)


def test_PolycubeSorter_try_add_polycube2():
    poly1 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, 0, 1)]),
        [(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, 0, 1)]
    )
    poly3 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, -1, 0)]),
        [(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, -1, 0)]
    )
    poly2 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (0, 2, 0)]),
        [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
    )
    sorter = PolycubeSorter()

    assert sorter.try_add_polycube(poly1)
    assert sorter.try_add_polycube(poly3) == False
    # assert sorter.try_add_polycube(poly2)


def test_PolycubeSorter_try_add_polycube_size4():
    poly1 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0)]),
        [(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0)]
    )
    poly2 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1)]),
        [(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1)]
    )
    poly3 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 1), (0, 0, 0), (1, 0, 0), (1, 1, 0)]),
        [(0, 0, 1), (0, 0, 0), (1, 0, 0), (1, 1, 0)]
    )
    poly4 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (0, 2, 0), (1, 2, 0)]),
        [(0, 0, 0), (0, 1, 0), (0, 2, 0), (1, 2, 0)]
    )
    poly5 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 2, 0)]),
        [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 2, 0)]
    )

    sorter = PolycubeSorter()

    print("try add poly1")
    assert sorter.try_add_polycube(poly1)
    print(sorter)

    print("try add poly2")
    assert sorter.try_add_polycube(poly2)
    print(sorter)

    print("try add poly3")
    assert sorter.try_add_polycube(poly3)
    print(sorter)

    print("try add poly5")
    assert sorter.try_add_polycube(poly5)

    print("try add poly4")
    assert sorter.try_add_polycube(poly4)

    print(sorter)

# endregion


if __name__ == "__main__":
    test_PolycubeSorter_try_add_polycube_size4()

    # test_has_equivalence()

    # test_PolycubeSorter_try_add_polycube()
    # test_PolycubeSorter_try_add_polycube2()
