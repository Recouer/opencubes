from __future__ import annotations
import copy
import numpy as np
import geometry_utils as gu
import numpy.typing as npt
from collections import Counter


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


