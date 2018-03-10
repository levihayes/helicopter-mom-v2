"""
Pretty dumb Dijkstra snake, but makes use of a bunch of handy-dandy utility
functions and classes I wrote, so good example usage for those interested.
:author Charlie
"""
import bottle
import logging
import time
from bottle import request
import numpy as np

import helicoptermom.lib.pathfinding as pathfinding
from helicoptermom.lib.heatmap import make_heatmap
from helicoptermom.lib.gameobjects import World
from helicoptermom.lib.utils import neighbors_of
from helicoptermom.lib.voronoi import d_matrices, voronoi_zone

app = bottle.app()


@app.post("/start")
def start():
    return {
        "name": "Helicopter Mom v2",
        "taunt": "I'm not angry, I'm just disappointed.",
        "color": "#F44336",
        "head_type": "tongue",
        "tail_type": "block-bum",
        "head_url": "https://s3-us-west-2.amazonaws.com/flx-editorial-wordpress/wp-content/uploads/2016/01/19133540/seinfeld.jpg"
    }


def vornoi_defense(world):
    # Calculate d matrices for every snake
    enemy_snakes = [snake for snake in world.snakes.values() if snake.id != world.you.id]
    snake_scores = d_matrices(world, enemy_snakes)

    # For each option, simulate snake move and calculate Vornoi zones
    highest_vornoi_area = -1
    highest_scoring_option = None
    for next_point in neighbors_of(world.you.head[0], world.you.head[1], world.map):
        in_voronoi_zone = voronoi_zone(world, snake_scores, next_point)

        vornoi_area = np.sum(in_voronoi_zone)
        if vornoi_area > highest_vornoi_area:
            highest_vornoi_area = vornoi_area
            highest_scoring_option = next_point

    return pathfinding.get_next_move(world.you.head, [highest_scoring_option])


def hungry_mode(world):
    """ Used when we need food. Dijkstra to nearest food. """
    distance, predecessor = pathfinding.dijkstra(world.map, world.you.head)

    # Create heat map to find desirable areas on board
    heatmap = make_heatmap(world, world.you)

    # Mask inaccessible parts of map, get next location
    hmap_masked = np.ma.masked_array(heatmap, distance == np.inf)
    next_space_ind = np.argmax(hmap_masked)

    ns_x = next_space_ind % world.width
    ns_y = int(next_space_ind / world.width)

    # Dijkstra to next space
    path = pathfinding.find_path_dijkstra(ns_x, ns_y, predecessor)
    return pathfinding.get_next_move(world.you.head, path)


@app.post("/move")
def move():
    world = World(request.json)

    longest_snake = max(world.snakes.values(), key=lambda s: s.length)
    if world.you.health < 60 or world.you.length < longest_snake.length:
        next_move = hungry_mode(world)
    else:
        next_move = vornoi_defense(world)

    return {
        "move": next_move
    }


@app.post("/end")
def end():
    return {}


if __name__ == "__main__":
    app.run(port=8000)
