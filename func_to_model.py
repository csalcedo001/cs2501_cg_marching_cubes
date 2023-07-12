import pickle
import numpy as np
from argparse import ArgumentParser

from marching_cubes import marching_cubes



def sphere(x, y, z, radius):
    return x ** 2 + y ** 2 + z ** 2 - radius ** 2

def wave(x, y, z):
    return np.sin(x) + np.sin(z)



parser = ArgumentParser()
parser.add_argument("--function", type=str, default="sphere")
parser.add_argument("--radius", type=float, default=1.5)
parser.add_argument("--plot_range_scale", type=float, default=2)
parser.add_argument("--threshold", type=float, default=0)
parser.add_argument("--step", type=float, default=1)

args = parser.parse_args()




bound = args.plot_range_scale * np.ones((3,))

if args.function == "sphere":
    f = lambda x, y, z: sphere(x, y, z, args.radius)
elif args.function == "wave":
    f = wave
else:
    raise ValueError("Invalid function name")



print("Scanning through", ((args.plot_range_scale * 2) // args.step) ** 3, "boxes")
triangles = marching_cubes(f, args.threshold, -bound, bound, args.step)
print("Shape of triangle mesh:", triangles.shape)

with open("model.pkl", "wb") as f:
    pickle.dump(triangles, f)