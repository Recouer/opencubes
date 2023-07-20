from __future__ import annotations
import copy
from collections import Counter
from polycube import PolyCube
from utils import has_equivalence


class Sorter:
    """
    this class is tasked with Sorting the polycube.
    it is a tree where each branch is defined by the path taken to get to this branch.
    a path is obtained from the get_parse function of the polycube class and returns 
    a list of integer that represents a path to get to all the cube inside the polycube.
    
    this path is used to determine the identity of a polycube and determine whether 
    a polycube is the same as another one.
    """

    def __init__(self, connection = 0, parent=None):
        self.parent = parent
        self.children: dict[any, Sorter] = dict()
        self.leaf_polycube = None
        self.connection = connection


    def __repr__(self):
        if self.leaf_polycube is not None:
            string = self.leaf_polycube.__repr__()
        else:
            string = self.children.__repr__()
        return string

    def __add_get_child(self, position: int) -> Sorter:
        """
        from a position, return the associated child node. if the node does not exist,
        create it too.
        
        Args:
            position: the position from the parse

        Returns: the associated child Sorter
        """
        child = self.children.get(position)
        if child is None:
            child = Sorter(position, self)
            self.children[position] = child

        return child

    def add_polycube(self, polycube: PolyCube, polyparse: list[int], eq_dict: dict[int, int]) -> bool:
        """
        add a polycube to the sorter
        
        Args:
            polycube:
            polyparse:
            eq_dict:

        Returns:

        """
        child = self
        for _parse in polyparse:
            polycube_parse = eq_dict[_parse] if eq_dict[_parse] != 0 else _parse
            child = child.__add_get_child(polycube_parse)
        if child.leaf_polycube is None:
            child.leaf_polycube = polycube
            return True
        return False


class PolycubeSorter:
    """
    this is the class in charge of Sorting the polycube inside a given polycube set.
    it possesses a Sorter that is a tree with each of its leaves being a polycube.
    if there exists a path inside a polycube starting by a cube with the same
    connectivity as starter_node, then that means the polycube already exists within
    the set, otherwise we add the polycube to the set.
    """

    def __init__(self):
        self.sorter: Sorter = Sorter()
        self.starter_node: int = -1

    def __repr__(self):
        string = f"starter node: {self.starter_node}\n"
        string += self.sorter.__repr__()
        return string

    def __is_inside_rec(self, sorter: Sorter, polycube: PolyCube, current_node: int, traversed_list: list[bool], current_parse: list, eq_list: dict[int, int]) -> bool:
        # TODO :    Change the function to check the paths inside the polycube instead of the paths
        #           inside the sorter using the paths of the polycubes
        sort_order = [1, 2, 4, 8, 16, 32]
        traversed_list[current_node] = True
        adjacencies = polycube.get_adjacencies(current_node)

        # if this is true, it means that we have explored all the possible adjacent cube
        # and that we need to backtrack in order to continue exploring the polycube.
        if all([traversed_list[traversed] for traversed in adjacencies.keys()]):
            for child in sorter.children.items():
                if isinstance(child[0], str):
                    # check that the backtracking is correct: that is, that we effectively need to backtrack the
                    # right amount of cubes in order to get the first cube with a connection to a nonexplored cube
                    backtrack: int = int(child[0].split(':')[1])
                    backtrack_node: int = current_node
                    backtracks_rec: int = 0
                    for i in range(len(current_parse)-1, len(current_parse) - 1 - backtrack):
                        index = i - backtracks_rec
                        while isinstance(current_parse[index], str):
                            backtracks_rec += int(current_parse[index].split(':')[1])
                            index = i - backtracks_rec

                        backtrack_node = polycube.get_adjacent_node(backtrack_node, current_parse[index])
                        adjacents = polycube.get_adjacencies(backtrack_node)
                        if not all([traversed_list[traversed] for traversed in adjacents.keys()]):
                            continue
                    self.__is_inside_rec(sorter, polycube, backtrack_node, traversed_list, current_parse, eq_list)
        
        # else we can still continue exploring without backtracking and thus we continue.
        else:
            for child in sorter.children.items():
                for adjacency, cube_index in adjacencies.items():
                    # in this case we have to check depending on the equivalence list if there is the next connection
                    # corresponding to the sort order and if it is not, it means that there is no correspondance 
                    # between all the polycube derived from that branchand the search can be stopped.
                    pass
        pass

    def try_add_polycube(self, polycube: PolyCube) -> bool:
        """
        check if the polycube is already present in the set and add it
        into itself if it is not inside.

        Args:
            polycube: the polycube to be added

        Returns: a boolean that tells if the polycube has been added into the set or not

        """

        if self.starter_node < 0:
            counter = Counter(polycube.cube_identity)
            # here the starter node is represented by the amount of connections it has
            self.starter_node = min(counter, key=counter.get)

            polycube_parses = [parses for parses in polycube.get_parses(self.starter_node)]
            sorter = self.sorter
            for _parse in polycube_parses[0]:
                sorter = sorter.__add_get_child(_parse)
            sorter.leaf_polycube = polycube

            return True

        else:
            polycube_parsers = polycube.get_parses(self.starter_node)
            can_be_added = True
            equivalence_list = dict({1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0})

            # one eq_list for each starting node
            final_eq_list: dict[any, int] = dict({1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0, "index": -1})
            for polycube_parse in polycube_parsers:
                final_eq_list["index"] = final_eq_list["index"] + 1
                if self.__is_inside_rec(self.sorter, polycube_parse, equivalence_list):
                    can_be_added = False

            if can_be_added:
                self.sorter.add_polycube(polycube, polycube_parsers[final_eq_list["index"]], final_eq_list)
                return True
            return False
