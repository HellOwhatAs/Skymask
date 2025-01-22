import cupy
from numpy.typing import NDArray
from scipy.spatial import KDTree
from typing import Tuple
if cupy.cuda.is_available():
    import cupy as np
    free_mem, total_mem = cupy.cuda.runtime.memGetInfo()
    np.get_default_memory_pool().set_limit(free_mem * 0.8)
    # https://docs.cupy.dev/en/stable/reference/generated/cupy.cuda.MemoryPool.html
else:
    import numpy as np

def select_lines(
        theta: NDArray[np.float64],
        lines: NDArray[np.float64],
        kdtree: KDTree,
        pos: Tuple[float, float] = (0, 0),
        max_dist = np.inf
    ) -> Tuple[NDArray[np.float64], NDArray[np.bool_]]:
    """
    Select lines based on the given angles.
    # Parameters:
    `theta`: array of angles with shape (m,).
        Each element shound be in range [0, pi)
    `lines`: array with shape (n, 6) where each row represents  
        a line defined by two points (x1, y1, z1, x2, y2, z2).
    `kdtree`: KDTree object built from `lines`.
    `pos`: the position of the observer.
    `max_dist`: select line within distance threshold.
    # Returns:
    `selected_lines`: array with shape (n_, 6) where each row is from `lines`.
    `selected_mask`: boolean array with shape (n_, m) indicating whether  
        each angle in `theta` falls within the angle range of each line.
    """
    idxs = kdtree.query_ball_point(pos, max_dist)
    lines = lines[idxs]

    xa, ya, xb, yb = (
        lines[:, 0] - pos[0], lines[:, 1] - pos[1],
        lines[:, 3] - pos[0], lines[:, 4] - pos[1]
    )
    lines = lines[(xb * ya) != (xa * yb)].copy()
    lines[:, (0, 3)] -= pos[0]
    lines[:, (1, 4)] -= pos[1]

    theta_a = np.arctan2(lines[:, 1], lines[:, 0])
    theta_b = np.arctan2(lines[:, 4], lines[:, 3])

    mask = theta_a > theta_b
    theta_a[mask], theta_b[mask] = theta_b[mask], theta_a[mask]

    mask = (theta_b - theta_a) < np.pi
    theta = np.expand_dims(theta, axis=0).repeat(lines.shape[0], axis=0)

    theta[mask, :] -= theta_a[mask, np.newaxis]
    theta_b[mask] -= theta_a[mask]

    mask = ~mask
    theta[mask, :] -= theta_b[mask, np.newaxis]
    theta_b[mask] = 2 * np.pi + theta_a[mask] - theta_b[mask]

    theta = np.fmod(np.fmod(theta, np.pi) + np.pi, np.pi)

    return lines, theta <= theta_b[:, np.newaxis]


def calc_alpha(
    theta: NDArray[np.float64],
    lines: NDArray[np.float64],
    selected: NDArray[np.bool_]
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Calculate angle of elevation based on theta and selected lines.
    # Parameters:
    `theta`: array of angles with shape (m,).
        Each element shound be in range [0, pi)
    `lines`: array with shape (n, 6) where each row represents  
        a line defined by two points (x1, y1, z1, x2, y2, z2).
    `selected`: boolean array with shape (n, m) indicating whether  
        each angle in `theta` falls within the angle range of each line.
    # Returns:
    `alpha_1`: shape (m,) array of angles of elevation  
        with respect to `theta`.
    `alpha_2`: shape (m,) array of angles of elevation  
        with respect to `theta - pi`.
    """
    if lines.shape[0] == 0:
        return np.zeros_like(theta), np.zeros_like(theta)

    alphas = selected * (
        np.arctan((
            (lines[:, 1] * lines[:, 5] - lines[:, 4] * lines[:, 2])
                .reshape((-1, 1))
            @ np.cos(theta).reshape((1, -1)) +
            (lines[:, 3] * lines[:, 2] - lines[:, 0] * lines[:, 5])
                .reshape((-1, 1))
            @ np.sin(theta).reshape((1, -1))
        ) / (lines[:, 3] * lines[:, 1] - lines[:, 0] * lines[:, 4])
                .reshape(-1, 1))
    )

    alpha_1: NDArray[np.float64] = np.maximum(alphas.max(axis=0), 0)
    alpha_2: NDArray[np.float64] = np.maximum(-alphas.min(axis=0), 0)
    return alpha_1, alpha_2


if __name__ == "__main__":
    from data_reader import build_kdtree

    lines = np.array([
        #  xa,   ya,   za,   xb,   yb,  zb
        [ 1.0,  1.0,  1.0, -1.0,  1.0, 1.0],
        [-1.0,  1.0,  1.0, -1.0, -1.0, 1.0],
        [-1.0, -1.0,  1.0,  1.0, -1.0, 1.0],
        [ 1.0, -1.0,  1.0,  1.0,  1.0, 1.0],
    ])
    kdtree = build_kdtree(lines)
    theta = np.linspace(0, np.pi, num=500, endpoint=False)

    selected_lines, selected = select_lines(theta, lines, kdtree, pos=(0.5, 0.2))
    a1, a2 = calc_alpha(theta, selected_lines, selected)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.yaxis.set_major_formatter("")
    x = np.concatenate((theta, (theta - np.pi), np.array([theta[0]])), axis=0)
    y= np.concatenate((np.pi/2 - a1, np.pi/2 - a2, np.array([np.pi/2 - a1[0]])), axis=0)
    if np.__name__ == "cupy":
        x, y = x.get(), y.get()
    ax.plot(x, y)
    ax.fill_between(x, y, np.pi/2, alpha=0.2)
    ax.set_ylim(0, np.pi / 2)
    plt.show()