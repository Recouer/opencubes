from utils import identity_to_tag, has_equivalence
import geometry_utils as gu
from polycube import PolyCube
from sorter import PolycubeSorter


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


def test():
    listy = [[(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, 2, 0)],
             [(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, 1, 1)],
             [(0, 0, 0), (0, 1, 0), (1, 0, 0), (-1, 1, 0)],
             [(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, 1, -1)],
             [(0, 0, 0), (0, 1, 0), (1, 0, 0), (2, 0, 0)],
             [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 0, 1)],
             [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, -1, 0)],
             [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 0, -1)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (0, 2, 0)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (1, 1, 0)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (0, 1, 1)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (-1, 1, 0)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (0, 1, -1)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (1, -1, 0)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (0, -1, 1)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (-1, -1, 0)],
             [(0, 0, 0), (0, 1, 0), (0, -1, 0), (0, -1, -1)]]

    sorter = PolycubeSorter()
    for coo in listy[9:11]:
        polycube = PolyCube(gu.get_adjacency_matrix_from_position_vector(coo), coo)
        sorter.try_add_polycube(polycube)

    print(sorter)

# endregion


if __name__ == "__main__":
    test()
    # test_PolycubeSorter_try_add_polycube_size4()

    # test_has_equivalence()

    # test_PolycubeSorter_try_add_polycube()
    # test_PolycubeSorter_try_add_polycube2()
