import pickle
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from argparse import ArgumentParser
from PIL import Image

from marching_cubes import marching_cubes



def grid_func(x, y, z, grid, interp, y_scale=1):
    x = int(x)
    y = int(y / y_scale)
    z = int(z)

    if x < 0 or x >= grid.shape[0]:
        return 0
    if y < 0 or y >= grid.shape[1]:
        return 0
    if z < 0 or z >= grid.shape[2]:
        return 0
    
    return interp([x, y, z])


parser = ArgumentParser()
parser.add_argument("--threshold", type=float, default=0.5)
parser.add_argument("--step", type=float, default=50)

args = parser.parse_args()


values = np.arange(5).reshape(1, 1, 5) + np.arange(5).reshape(1, 5, 1) + np.arange(5).reshape(5, 1, 1)
values = values ** 2
values = values / np.max(values)

tomo = []
for i in range(20, 40):
    img_path = f'data/mri_{i}.bmp'
    img = np.array(Image.open(img_path))
    tomo.append(img)
tomo = np.array(tomo)
print("Tomography shape:", tomo.shape)

grid = tomo.mean(axis=3)                # Gray scale
grid = grid / 255                       # [0, 1] range
grid = np.transpose(grid, (1, 0, 2))    # Transpose to match the orientation of the MRI
print("Grid shape:", grid.shape)


y_scale = 10

x_idx = np.arange(grid.shape[0])
y_idx = np.arange(grid.shape[1])
z_idx = np.arange(grid.shape[2])
interp = RegularGridInterpolator((x_idx, y_idx, z_idx), grid)

lower_bound = np.zeros((3,))
upper_bound = np.ones((3,)) * (np.array(grid.shape) - 1)
upper_bound[1] *= y_scale

f = lambda x, y, z: grid_func(x, y, z, grid, interp, y_scale=y_scale)


triangles = marching_cubes(f, args.threshold, lower_bound, upper_bound, step=args.step) / args.step
print("Shape of triangle mesh:", triangles.shape)

with open("model.pkl", "wb") as f:
    pickle.dump(triangles, f)