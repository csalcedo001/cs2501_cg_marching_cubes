import pickle
import numpy as np
from argparse import ArgumentParser

from marching_cubes import marching_cubes



def grid_func(x, y, z, grid):
    x = int(x)
    y = int(y)
    z = int(z)

    if x < 0 or x >= grid.shape[0]:
        return 0
    if y < 0 or y >= grid.shape[1]:
        return 0
    if z < 0 or z >= grid.shape[2]:
        return 0
    
    return grid[x, y, z]


parser = ArgumentParser()
parser.add_argument("--threshold", type=float, default=0.5)

args = parser.parse_args()


values = np.arange(5).reshape(1, 1, 5) + np.arange(5).reshape(1, 5, 1) + np.arange(5).reshape(5, 1, 1)
values = values ** 2
values = values / np.max(values)

grid = values


lower_bound = np.zeros((3,))
upper_bound = np.ones((3,)) * (np.array(grid.shape) - 1)

f = lambda x, y, z: grid_func(x, y, z, grid)


triangles = marching_cubes(f, args.threshold, lower_bound, upper_bound, step=1)
print("Shape of triangle mesh:", triangles.shape)

with open("model.pkl", "wb") as f:
    pickle.dump(triangles, f)