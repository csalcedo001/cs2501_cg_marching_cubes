import pickle
import numpy as np
from argparse import ArgumentParser
from PIL import Image

from marching_cubes import marching_cubes



def grid_func(x, y, z, grid, y_scale=1):
    x = int(x)
    y = int(y / y_scale)
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
parser.add_argument("--step", type=float, default=15)

args = parser.parse_args()


values = np.arange(5).reshape(1, 1, 5) + np.arange(5).reshape(1, 5, 1) + np.arange(5).reshape(5, 1, 1)
values = values ** 2
values = values / np.max(values)

tomo = []
for i in range(40):
    img_path = f'data/mri_{i}.bmp'
    img = np.array(Image.open(img_path))
    tomo.append(img)
tomo = np.array(tomo)
print("Tomography shape:", tomo.shape)

grid = tomo.mean(axis=3)                # Gray scale
grid = grid / 255                       # [0, 1] range
grid = np.transpose(grid, (1, 0, 2))    # Transpose to match the orientation of the MRI
print("Grid shape:", grid.shape)


lower_bound = np.zeros((3,))
upper_bound = np.ones((3,)) * (np.array(grid.shape) - 1)

f = lambda x, y, z: grid_func(x, y, z, grid, y_scale=5)


triangles = marching_cubes(f, args.threshold, lower_bound, upper_bound, step=args.step)
print("Shape of triangle mesh:", triangles.shape)

with open("model.pkl", "wb") as f:
    pickle.dump(triangles, f)