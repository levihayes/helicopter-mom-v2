"""
heatmap.py
Functions for constructing a "heat map" of the game world. Areas near food will
be hotter, and areas near snake heads will be colder.
For use with the snake's 'hungry mode'.
"""

import numpy as np
from helicoptermom.lib.utils import check_in_bounds


def make_heatmap(world, you):
    """Constructs a matrix of heat map scores for the world. The highest
    scoring area indicates the most desirable. -1 indicates an inaccessible
    zone.

    :param world: World to map.
    :param you: Snake to create a heat map around.
    :return: Numpy matrix of heat map scores.
    """
    map = np.full((world.height, world.width), 0, dtype=np.int32)

    # mark food
    for loc in world.food:
        _mark_zone(map, loc, 4)

    enemy_heads = [snake.head for snake in world.snakes.values()
                   if snake.id != you.id]
    for head in enemy_heads:
        _mark_zone(map, head, -4)

    # mark inaccessible zones
    for s in world.snakes.values():
        for x, y in s.body:
            map[y][x] = -1

    return map


def _mark_zone(map, loc, weight, decay_rate=2):
    """Mark a zone with a given weight. Tiles farther out from the original
    zone will be marked with exponentially decaying values until the weight
    hits 1.

    Run time O(log base decay_rate of weight)

    :param map: Map to be marked
    :param loc: "Ground zero" for the mark. Values will be marked around this
                 zone depending on the decay rate (x, y).
    :param weight: Initial weight
    :param decay_rate: Mark weights will be divided by this value for each unit
                       the marks radiate outward.

    ex. Weight 4, decay rate 2
        1 1 1 1 1
        1 2 2 2 1
        1 2 4 2 1
        1 2 2 2 1
        1 1 1 1 1
    """
    radius = 0
    mark_weight = weight
    while abs(mark_weight) != 1:

        # mark top and bottom edges
        x_offset = -radius
        while x_offset <= radius:

            if check_in_bounds(loc[0] + x_offset, loc[1] - radius, map):
                map[loc[1] - radius][loc[0] + x_offset] += mark_weight

            if check_in_bounds(loc[0] + x_offset, loc[1] + radius, map):
                map[loc[1] + radius][loc[0] + x_offset] += mark_weight

            x_offset += 1

        # mark left and right edges
        y_offset = -radius
        while y_offset <= radius:

            if check_in_bounds(loc[0] - radius, loc[1] + y_offset, map):
                map[loc[1] + y_offset][loc[0] - radius] += mark_weight

            if check_in_bounds(loc[0] + radius, loc[1] + y_offset, map):
                map[loc[1] + y_offset][loc[0] + radius] += mark_weight

            y_offset += 1

        radius += 1
        mark_weight = int(mark_weight / decay_rate)
