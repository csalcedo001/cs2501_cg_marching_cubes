import numpy as np
import json

CUBE_CORNERS = np.array([
    [0, 0, 0],
    [1, 0, 0],
    [0, 1, 0],
    [1, 1, 0],
    [0, 0, 1],
    [1, 0, 1],
    [0, 1, 1],
    [1, 1, 1],
])

def marching_cubes(f, lower, upper, step):
    """
    Marching cubes algorithm for isosurface extraction.

    Args:
    - f: function to extract
    - lower: lower bounds of range (x, y, z)
    - upper: upper bounds of range (x, y, z)
    - step: step size (same for all axes)

    Returns:
    - vertices: list of vertices
    - faces: list of faces
    """

    shape = (upper - lower) // step

    x_points = np.linspace(lower[0], lower[0] + step * shape[0], shape[0])
    y_points = np.linspace(lower[1], lower[1] + step * shape[1], shape[1])
    z_points = np.linspace(lower[2], lower[2] + step * shape[2], shape[2])

    values = np.zeros(shape)
    for i, x in enumerate(x_points):
        for j, y in enumerate(y_points):
            for k, z in enumerate(z_points):
                values[i, j, k] =  f(x, y, z)
    
    return values

def get_values_from_function(f, x_points, y_points, z_points):
    shape = (len(x_points), len(y_points), len(z_points))

    values = np.zeros(shape)
    for i, x in enumerate(x_points):
        for j, y in enumerate(y_points):
            for k, z in enumerate(z_points):
                values[i, j, k] = f(x, y, z)
    
    return values

def get_triangles_from_values(values, scale, threshold):
    triangles = []

    for i in range(values.shape[0] - 1):
        for j in range(values.shape[1] - 1):
            for k in range(values.shape[2] - 1):
                ref_idx = np.array([i, j, k])
                point_idx = CUBE_CORNERS + ref_idx

                corners = values[point_idx]
                signs = corners > threshold

                case_idx = int(np.sum(2 ** signs))
                case_triangles = TRIANGLE_CASES[case_idx]
                case_triangles *= scale
                case_triangles += ref_idx

                triangles += case_triangles.tolist()
    
    return triangles

def get_case_table(table_of_case_vertices):
    table_of_case_triangles = []
    for case_vertices in table_of_case_vertices:
        raw_case_triangles = np.split(case_vertices, 3)

        case_triangles = []
        for triangle in raw_case_triangles:
            if triangle[0] == -1:
                break
            
            case_triangles.append(triangle)
        
        table_of_case_triangles.append(case_triangles)
    
    return table_of_case_triangles


with open("triangles.json", "r") as f:
    table_of_case_vertices = np.array(json.load(f))

TRIANGLE_CASES = get_case_table(table_of_case_vertices)