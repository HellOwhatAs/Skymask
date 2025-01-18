import numpy as np
# import cupy as np
from numpy.typing import NDArray

def select_lines(theta: NDArray[np.float64], lines: NDArray[np.float64]):
    """
    Select lines based on the given angles.
    # Parameters:
    - theta: array of angles with shape (m,).
      Each element shound be in range [0, pi)
    - lines: array with shape (n, 6) where each row represents  
      a line defined by two points (x1, y1, z1, x2, y2, z2).
    # Returns:
    - np.ndarray: boolean array with shape (n, m) indicating whether  
      each angle in `theta` falls within the angle range of each line.
    """
    theta_a = np.arctan2(lines[:, 1], lines[:, 0])
    theta_b = np.arctan2(lines[:, 4], lines[:, 3])

    mask = theta_a > theta_b
    theta_a[mask], theta_b[mask] = theta_b[mask], theta_a[mask]

    delta = theta_b - theta_a
    mask1, mask2, mask3 = delta < np.pi, delta > np.pi, delta == np.pi

    theta = np.expand_dims(theta, axis=0).repeat(lines.shape[0], axis=0)

    theta[mask1, :] -= theta_a[mask1, np.newaxis]
    theta_b[mask1] -= theta_a[mask1]
    theta_a[mask1] = 0

    theta[mask2, :] -= theta_b[mask2, np.newaxis]
    theta_b[mask2] = 2 * np.pi + theta_a[mask2] - theta_b[mask2]
    theta_a[mask2] = 0

    theta[mask3] = 0
    theta_b[mask3] = 0
    theta_a[mask3] = 0

    theta = np.fmod(np.fmod(theta, np.pi) + np.pi, np.pi)

    return theta <= theta_b[:, np.newaxis]


def calc_alpha(
    theta: NDArray[np.float64], lines: NDArray[np.float64], selected: NDArray[np.bool_]
):
    """
    Calculate angle of elevation based on theta and selected lines.
    # Parameters:
    - theta: array of angles with shape (m,).
      Each element shound be in range [0, pi)
    - lines: array with shape (n, 6) where each row represents  
      a line defined by two points (x1, y1, z1, x2, y2, z2).
    - selected: boolean array with shape (n, m) indicating whether  
      each angle in `theta` falls within the angle range of each line.
    # Returns:
    - alpha_1: shape (m,) array of angles of elevation  
      with respect to `theta`.
    - alpha_2: shape (m,) array of angles of elevation  
      with respect to `theta - pi`.
    """
    alphas = selected * (
        np.arctan((
            (lines[:, 1] * lines[:, 5] - lines[:, 4] * lines[:, 2])
                .reshape((-1, 1))
            @ np.cos(theta).reshape((1, -1)) +
            (lines[:, 3] * lines[:, 2] - lines[:, 0] * lines[:, 5])
                .reshape((-1, 1))
            @ np.sin(theta).reshape((1, -1))
        ) / (lines[:, 3] * lines[:, 1] - lines[:, 0] * lines[:, 4])[:, np.newaxis]
        )
    )

    alpha_1: NDArray[np.float64] = np.maximum(alphas.max(axis=0), 0)
    alpha_2: NDArray[np.float64] = np.maximum(-alphas.min(axis=0), 0)
    return alpha_1, alpha_2


if __name__ == "__main__":
    lines = np.array([
        #  xa,   ya,   za,   xb,   yb,  zb
        [ 1.0,  1.0,  1.0, -1.0,  1.0, 1.0],
        [-1.0,  1.0,  1.0, -1.0, -1.0, 1.0],
        [-1.0, -1.0,  1.0,  1.0, -1.0, 1.0],
        [ 1.0, -1.0,  1.0,  1.0,  1.0, 1.0],
    ])

    theta = np.linspace(0, np.pi, num=500, endpoint=False)

    selected = select_lines(theta, lines)

    a1, a2 = calc_alpha(theta, lines, selected)
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.yaxis.set_major_formatter("")
    ax.plot(theta, np.pi/2 - a1)
    ax.plot((theta - np.pi), np.pi/2 - a2)
    ax.set_ylim(0, np.pi / 2)
    plt.show()