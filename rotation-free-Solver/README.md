# Rotation-Free implementation of polycubes

This is a rotation free implementation of Mickael Pound's opencube project.
The idea behind this implementation was to use an adjacency graphs in order 
to represent the cubes instead of its 3D representation.

the advantage of using an adjacency graph instead of a Tensor is of course
the dimensionality of the stored values. while 



there is an issue with the current implementation:
i did the search inside the graph in reverse.
the get_parses function from the polycube class should not exist.
instead we should look for every 