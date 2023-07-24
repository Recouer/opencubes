from __future__ import annotations
import copy
from collections import Counter
from polycube import PolyCube
from utils import has_equivalence
from geometry_utils import get_opposite


class Sorter:
    """
    this class is tasked with Sorting the polycube.
    it is a tree where each branch is defined by the path taken to get to this branch.
    a path is obtained from the get_parse function of the polycube class and returns 
    a list of integer that represents a path to get to all the cube inside the polycube.
    
    this path is used to determine the identity of a polycube and determine whether 
    a polycube is the same as another one.
    """

    def __init__(self, connection=-1, parent=None):
        self.parent: Sorter = parent
        self.children: dict[any, Sorter] = dict()
        self.leaf_polycube: any = None
        self.connection: int = connection

    def __repr__(self):
        if self.leaf_polycube is not None:
            string = self.leaf_polycube.__repr__()
        else:
            string = self.children.__repr__()
        return string

    def show_path(self, path: str = "") -> str:
        parent = self
        while parent is not None:
            path = f"{parent.connection} " + path
            parent = parent.parent

        return path

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
        child = self
        print(self)
        print("adding polycube")
        for _parse in polyparse:
            print("parse: ", _parse)
            child = child.__add_get_child(_parse)
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

    def __is_inside_rec(self, sorter: Sorter, polycube: PolyCube, current_node: int, traversed_list: list[bool],
                        current_parse: list, eq_list: dict[int, int],
                        final_eq_list: dict[int, int], depth: int = 0, max_depth: int = 0) -> bool:
        print()
        print("######################################################")
        sort_order = [1, 2, 4, 8, 16, 32]
        traversed_list[current_node] = True
        adjacencies = polycube.get_adjacencies(current_node)
        print(current_node, adjacencies, eq_list)
        print("trace :" + sorter.show_path())
        print(current_parse)
        print(f"current node : {current_node}")

        is_inside = False

        if depth > max_depth:
            for key, value in eq_list.items():
                final_eq_list[key] = value
            max_depth = depth

        if all(traversed_list):
            print("traversed all")
            print(self.sorter.show_path())
            return True

        # if this is true, it means that we have explored all the possible adjacent cube
        # and that we need to backtrack in order to continue exploring the polycube.
        is_neighbor_traversed = [traversed_list[traversed] for traversed in adjacencies.values()]
        if is_neighbor_traversed and all(is_neighbor_traversed):
            print(adjacencies.items())
            print(traversed_list)
            print("backtracking")
            for child in sorter.children.items():
                print(child)
                if isinstance(child[0], str):
                    # check that the backtracking is correct: that is, that we effectively need to backtrack the
                    # right amount of cubes in order to get the first cube with a connection to a nonexplored cube
                    backtrack: int = int(child[0].split(':')[1])
                    backtrack_node: int = current_node
                    backtracks_rec: int = 0
                    print(f"backtrack_node: {backtrack_node} ", backtrack)
                    for i in range(len(current_parse) - 1, len(current_parse) - 1 - backtrack, -1):
                        index = i - backtracks_rec
                        print(current_parse, current_parse[index])
                        while isinstance(current_parse[index], str):
                            backtracks_rec += int(current_parse[index].split(':')[1])
                            index = i - backtracks_rec

                        print("test", backtrack_node, current_parse[index])

                        adjacency = 0
                        for key, value in eq_list.items():
                            if value == get_opposite(current_parse[index]):
                                adjacency = key
                        backtrack_node = polycube.get_adjacent_node(backtrack_node, adjacency)
                        print(f"backtrack_node: {backtrack_node}")

                    new_traversed_list = copy.deepcopy(traversed_list)
                    if isinstance(current_parse[-1], str):
                        parse: str = current_parse.pop(len(current_parse) - 1)
                        parse = f"BT:{int(parse.split(':')[0]) + 1}"
                        current_parse.append(parse)
                    else:
                        current_parse.append("BT:1")
                    is_inside |= self.__is_inside_rec(child[1], polycube, backtrack_node, new_traversed_list,
                                                      current_parse, eq_list,
                                                      final_eq_list, depth + 1, max_depth)
                    print(is_inside)

        # else we can still continue exploring without backtracking and thus we continue.
        else:
            print("continuing forward")
            # in this case we have to check depending on the equivalence list if there is the next connection
            # corresponding to the sort order and if it is not, it means that there is no correspondence
            # between all the polycube derived from that branch and thus the search can be stopped.

            # if we find a correspondence between the first element of the sorter and an unexplored cube
            # then we update the equivalence list and continue inside
            possible_child = []

            for key, value in sorter.children.items():
                if isinstance(key, int):
                    for adja in polycube.get_adjacencies(current_node).items():
                        if eq_list[adja[0]] != 0:
                            if eq_list[adja[0]] == key and not traversed_list[adja[1]]:
                                possible_child += [key]
                                break
                        else:
                            possible_child += [key]

            print("possible child : ", possible_child)
            if not possible_child:
                return False

            minimum_sorter: int = min(possible_child)

            for adja in polycube.get_adjacencies(current_node).items():
                print(adja, eq_list[adja[0]], minimum_sorter, traversed_list[adja[1]])
                if eq_list[adja[0]] != 0 and not traversed_list[adja[1]] and eq_list[adja[0]] == minimum_sorter:
                    current_parse += [minimum_sorter]
                    new_node = polycube.get_adjacent_node(node=current_node, adjacency=adja[0])
                    new_traversed_list = copy.deepcopy(traversed_list)
                    print(minimum_sorter)
                    is_inside |= self.__is_inside_rec(sorter.children[minimum_sorter], polycube, new_node,
                                                      new_traversed_list, current_parse, eq_list,
                                                      final_eq_list, depth + 1, max_depth)
                    print(is_inside)
                    break
                else:
                    print("no equivalence")

            possible_connection_equivalences = dict([adja for adja in polycube.get_adjacencies(current_node).items()
                                                     if eq_list[adja[0]] == 0 and not traversed_list[adja[1]]])

            for connection in possible_connection_equivalences.keys():
                new_eq_list = copy.deepcopy(eq_list)
                print("new eq list : ", new_eq_list)
                if has_equivalence(connection, minimum_sorter, new_eq_list):
                    print("new eq list : ", new_eq_list)
                    new_node = possible_connection_equivalences[connection]
                    current_parse += [minimum_sorter]
                    new_traversed_list = copy.deepcopy(traversed_list)
                    is_inside |= self.__is_inside_rec(sorter.children[minimum_sorter], polycube, new_node,
                                                      new_traversed_list, current_parse,
                                                      new_eq_list, final_eq_list, depth, max_depth)
                    print("returned from adding eq " + f"{is_inside}")

        print("finished looking")
        return is_inside

    def try_add_polycube(self, polycube: PolyCube) -> bool:
        """
        check if the polycube is already present in the set and add it
        into itself if it is not inside.

        Args:
            polycube: the polycube to be added

        Returns: a boolean that tells if the polycube has been added into the set or not

        """

        if self.starter_node < 0:
            counter: dict[int, int] = Counter(polycube.cube_identity)
            # here the starter node is represented by the amount of connections it has
            self.starter_node = min(counter, key=counter.get)

            polycube_parses = [parses for parses in polycube.get_parses(self.starter_node)]
            if polycube_parses:
                self.sorter.add_polycube(polycube, polycube_parses[0],
                                     eq_dict={1: 1, 2: 2, 4: 4, 8: 8, 16: 16, 32: 32})
            else:
                self.sorter.add_polycube(polycube, [],
                                     eq_dict={1: 1, 2: 2, 4: 4, 8: 8, 16: 16, 32: 32})


            return True

        else:
            can_be_added = True
            equivalence_list = dict({1: 0, 2: 0, 4: 0, 8: 0, 16: 0, 32: 0})
            final_eq_list: dict[any, int] = dict()
            max_depth = 0
            final_cube = -1

            print()
            for cube in polycube.get_nodes_with_NAdjacencies(self.starter_node):
                print()
                old_max_depth = max_depth
                new_eq_list: dict[int, int] = dict()
                print(self.sorter)
                print(polycube)
                is_inside = self.__is_inside_rec(self.sorter, polycube, cube,
                                                 [False for _ in range(len(polycube.adjacency_matrix))],
                                                 [], equivalence_list, new_eq_list, max_depth=max_depth)
                if is_inside:
                    can_be_added = False
                    print("!!!!!!!!!!!!!!!!!!!  CANNOT BE ADDED !!!!!!!!!!!!!!!!!!!!!!!!")
                    print(new_eq_list, is_inside)

                if old_max_depth <= max_depth:
                    for key, value in new_eq_list.items():
                        final_eq_list[key] = value
                    final_cube = cube

            if can_be_added:
                for key, value in equivalence_list.items():
                    if not final_eq_list.get(key):
                        final_eq_list[key] = value

                parse = polycube.get_parse_from_cube(final_cube)
                self.sorter.add_polycube(polycube, parse, final_eq_list)
                return True
            return False
