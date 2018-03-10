"""
Functions for calculating a snake's 'Voronoi zone'.
A snake's voronoi zone is the matrix of points which a snake can get to
before any other snakes on the board.
"""
import numpy as np
from helicoptermom.lib.pathfinding import dijkstra


def d_matrices(world, snakes):
    """Get the distance matrices for a given array of snakes.

    :return {
        snake_id: matrix,
        ...
    }
    """
    matrices = {}
    for snake in snakes:
        d, p = dijkstra(world.map, snake.head)
        matrices.update({snake.id : d})

    return matrices


def voronoi_zone(world, d_matrices, snake_head):
    """Get the 'Voronoi zone' for a given snake.

    :param d_matrices Dijkstra scores for all snakes to consider, not including
                      the snake referred to by snake_head.
    :param snake_head Point to calculate voronoi zone for.

    :return Dijkstra scores for snake, Voronoi zone as an np.array of booleans
    """
    snake_d, snake_p = dijkstra(world.map, snake_head)
    in_vornoi_zone = np.full((world.height, world.width), True, dtype=np.bool)

    # Get all points in your Vornoi zone
    for val in d_matrices.values():
        in_vornoi_zone = np.logical_and(in_vornoi_zone, val - snake_d > 0)

    return snake_d, snake_p, in_vornoi_zone
