from __future__ import annotations
import copy
import numpy as np
import geometry_utils as gu
import numpy.typing as npt
from collections import Counter
from sorter import PolycubeSorter
from polycube import PolyCube


def has_equivalence(connection: int, _parse: int, eq_list: dict):
    """
    test if there is an equivalence between the value connection and _parse using eq_list.
    if there are no equivalence for _parse and connection does not already have one,
    create an equivalence between connection and _parse, as well as their opposite and return true
    if connection has an equivalence with _parse, also return true.
    in any other case, return false.

    Args:
        connection:
        _parse:
        eq_list: the list of equivalence

    Returns: true if there is an equivalence, false otherwise.

    """
    if _parse in eq_list.values() and (eq_list[connection] != _parse):
        return False

    if eq_list[connection] == 0:
        eq_list[connection] = _parse
        eq_list[gu.get_opposite(connection)] = gu.get_opposite(_parse)
        return True

    return eq_list[connection] == _parse


def identity_to_tag(identity: npt.NDArray):
    """
    from the identity of a polycube, return its associated tag

    Args:
        identity: the identity of a polycube

    Returns: a tag

    """
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


def update_adjacency_matrix(adjacency_matrix, position_vector) -> None:
    """
    this function is used after appending a value to the adjacency matrix to check for
    any collision with another cube from the polycube


    Args:
        adjacency_matrix: the adjacency matrix from the polycube
        position_vector: the position vector of the polycube
    """
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


class PolycubeHolder:
    """
    the structure that holds the polycube depending on their tags
    """

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
