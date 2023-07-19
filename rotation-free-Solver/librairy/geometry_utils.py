import numpy as np


def get_adjacency_matrix_from_position_vector(position_vector: list[tuple[int, int, int]]):
    adjacency_matrix = np.zeros((len(position_vector), len(position_vector)))
    for node in range(len(position_vector)):
        for neighbor in range(node + 1, len(position_vector)):
            try:
                adjacency = get_adjacency_from_positions(position_vector[node], position_vector[neighbor])
                adjacency_matrix[neighbor][node] = adjacency
                adjacency_matrix[node][neighbor] = get_opposite(adjacency)
            except ArithmeticError:
                continue
    return adjacency_matrix


def iterate_through(adjacency: int):
    if adjacency >= 64:
        return ArithmeticError

    value = 1
    while adjacency > 0:
        if adjacency % 2 == 1:
            yield value
            adjacency = (adjacency - 1) / 2
            value *= 2
        else:
            adjacency /= 2
            value *= 2


def get_opposite(face: int):
    return int(2 ** ((np.log2(face) + 3) % 6))


def get_number_of_neighbors(cube):
    value = 0
    while cube > 0:
        if cube % 2 == 1:
            cube = (cube - 1) / 2
            value += 1
        else:
            cube /= 2
    return value


def get_position_from_adjacency(initial_position, adjacency: int):
    if adjacency == 1:
        return [(initial_position[0], initial_position[1] + 1, initial_position[2])]
    if adjacency == 2:
        return [(initial_position[0] + 1, initial_position[1], initial_position[2])]
    if adjacency == 4:
        return [(initial_position[0], initial_position[1], initial_position[2] + 1)]
    if adjacency == 8:
        return [(initial_position[0], initial_position[1] - 1, initial_position[2])]
    if adjacency == 16:
        return [(initial_position[0] - 1, initial_position[1], initial_position[2])]
    if adjacency == 32:
        return [(initial_position[0], initial_position[1], initial_position[2] - 1)]


def get_adjacency_from_positions(origin, destination):
    diff = tuple(np.array(origin) - np.array(destination))
    if sum([abs(value) for value in diff]) > 1:
        raise ArithmeticError

    if diff == (1, 0, 0):
        return 2
    if diff == (0, 1, 0):
        return 1
    if diff == (0, 0, 1):
        return 4
    if diff == (-1, 0, 0):
        return 16
    if diff == (0, -1, 0):
        return 8
    if diff == (0, 0, -1):
        return 32


if __name__ == "__main__":
    for i in iterate_through(54):
        print(i)

    print(get_adjacency_matrix_from_position_vector([(0, 0, 0), (0, 1, 0), (0, 2, 0)]))
