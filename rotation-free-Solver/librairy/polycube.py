from __future__ import annotations
import copy
import numpy as np
import geometry_utils as gu
import numpy.typing as npt
from collections import Counter
from utils import update_adjacency_matrix

sort_order = [1, 2, 4, 8, 16, 32]


def create_parse_rec(adjacency_matrix: npt.NDArray,
                     parse_list: list[any],
                     node: int,
                     backtrack: int,
                     traversed_node: list[bool],
                     eq_list: dict[int, int]) -> int:
    traversed_node[node] = True
    adjacency_list = dict(
        [(eq_list[adjacency], i) for (i, adjacency) in enumerate(adjacency_matrix[node]) if adjacency != 0]
    )
    # error with the backtracking values
    for adjacency in sort_order:
        if adjacency in adjacency_list.keys() and not traversed_node[adjacency_list[adjacency]]:
            if backtrack > 0:
                parse_list.append(f"BT:{backtrack}")
                backtrack = 0

            parse_list.append(adjacency)
            backtrack = create_parse_rec(adjacency_matrix, parse_list, adjacency_list[adjacency], backtrack,
                                         traversed_node, eq_list)
            backtrack += 1
    return backtrack


class PolyCube:
    """
    this is the class that represents the polycube.
    it possesses an adjacency matrix, as well as a coo of all the positions of the cube inside the polycube
    """

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

    def get_nodes_with_NAdjacencies(self, adjacencies: int):
        return [index for index in range(len(self.cube_identity)) if self.cube_identity[index] == adjacencies]

    def get_adjacent_node(self, node: int, adjacency: int):
        for _adjacency, neighbor in self.get_adjacencies(node).items():
            if _adjacency == adjacency:
                return neighbor

        raise ValueError("no cube with such adjacency in the polygraph")

    def get_adjacencies(self, node_index: int) -> dict[int, int]:

        print("get adjacencies: ", self.adjacency_matrix[node_index], node_index)

        return dict(
            [(adjacency, i) for (i, adjacency) in enumerate(self.adjacency_matrix[node_index]) if adjacency != 0]
        )

    def get_3D_representation(self) -> np.ndarray:
        vector = np.array(self.position_vector)
        dims = [max(vector[:, coordinates]) - min(vector[:, coordinates]) + 1
                for coordinates in range(3)]
        mins = [min(vector[:, coordinates]) for coordinates in range(3)]

        threed_tensor = np.zeros(dims)
        for cube in self.position_vector:
            threed_tensor[cube[0] - mins[0],
                          cube[1] - mins[1],
                          cube[2] - mins[2]] = 1

        return threed_tensor

    def get_parse_from_cube(self, cube: int, eq_list: dict[int, int] = []):
        parse_list = []
        if not eq_list:
            eq_list = dict({1: 1, 2: 2, 4: 4, 8: 8, 16: 16, 32: 32})
        create_parse_rec(self.adjacency_matrix, parse_list, cube, 0,
                         [False for _ in range(len(self.adjacency_matrix))], eq_list)
        print("using cube :", cube)
        return parse_list

    def get_parses(self, starter_nodes: int):
        """
        this function is used to return a path inside the polycube.
        it is used when creating a new polycube holder when instantiating the Sorter.

        Args:
            starter_nodes:  the number of adjacent nodes (or connectivity)
                            of the nodes used in order to create the parse

        Returns: a path inside the node starting from a polycube with starter_nodes neighbor

        """

        if self.__parses:
            returned_parses = copy.deepcopy(self.__parses)
            return returned_parses

        indexes = self.get_nodes_with_NAdjacencies(starter_nodes)
        if not indexes:
            raise AttributeError("starter node not present into the polycube")

        for index in indexes:
            parse_list = []
            create_parse_rec(self.adjacency_matrix, parse_list, index, 0,
                             [False for _ in range(len(self.adjacency_matrix))],
                             dict(dict({1: 1, 2: 2, 4: 4, 8: 8, 16: 16, 32: 32})))
            if parse_list:
                if isinstance(parse_list[len(parse_list) - 1], str):
                    parse_list.pop(len(parse_list) - 1)
                if parse_list not in self.__parses:
                    self.__parses += [copy.deepcopy(parse_list)]

        returned_parses = copy.deepcopy(self.__parses)
        return returned_parses

    def __create_PCPO(self):
        return np.pad(self.adjacency_matrix, (1, 1))[1:, 1:]

    def iterate_through_All_PCPO(self):
        """
        from a polycube, we get all the PolyCube of size n Plus One (PCPO)

        Returns: an iterator of all the polycube of size n+1 that can be generated from the given polycube
        """
        for i in range(self.size):
            available_space = 63 - np.sum(self.adjacency_matrix[i])
            for position in gu.iterate_through(available_space):
                new_adjacency_matrix = self.__create_PCPO()
                new_adjacency_matrix[i, self.size] = position
                new_adjacency_matrix[self.size, i] = gu.get_opposite(position)

                new_position_vector = copy.deepcopy(self.position_vector)
                new_position_vector += gu.get_position_from_adjacency(self.position_vector[i], position)

                update_adjacency_matrix(new_adjacency_matrix, new_position_vector)

                yield PolyCube(new_adjacency_matrix, new_position_vector)


if __name__ == "__main__":
    poly1 = PolyCube(
        gu.get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0)]),
        [(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0)]
    )

    print(poly1.get_adjacencies(0))
    print(poly1.cube_identity)
    print(poly1.get_parses(2))
    print(poly1.get_3D_representation())

    pass
