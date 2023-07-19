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

    def __init__(self):
        self.children: dict[int, Sorter] = dict()
        self.leaf_polycube = None

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
            child = Sorter()
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

    def __is_inside_rec(self, sorter: Sorter, poly_parse: list[int], eq_list: dict[int, int]) -> bool:
        # TODO :    Change the function to check the paths inside the polycube instead of the paths
        #           inside the sorter using the paths of the polycubes

        if len(poly_parse) > 0:
            connection = poly_parse.pop(0)
            return_value = False
            for (child, child_sorter) in sorter.children.items():
                new_list = copy.deepcopy(eq_list)
                if has_equivalence(connection, child, new_list):
                    return_value |= self.__is_inside_rec(child_sorter, copy.deepcopy(poly_parse), new_list)
            return return_value
        else:
            return True

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
            final_eq_list: dict[any, int] = dict({1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0, "index": -1})
            for polycube_parse in polycube_parsers:
                final_eq_list["index"] = final_eq_list["index"] + 1
                if self.__is_inside_rec(self.sorter, polycube_parse, equivalence_list):
                    can_be_added = False

            if can_be_added:
                self.sorter.add_polycube(polycube, polycube_parsers[final_eq_list["index"]], final_eq_list)
                return True
            return False
