import skymask_py
import numpy as np
import time
from data_reader import build_kdtree
from skymask import select_lines, calc_alpha
import skymask
import cupy as cp


def bench_rust_par(world: skymask_py.World, poss, x):
    start = time.time()
    np.pi / 2 - world.par_samples(poss, x)
    return len(poss) / (time.time() - start)


def bench_rust(world: skymask_py.World, poss, x):
    start = time.time()
    [np.pi / 2 - world.skymask(pos).samples(x) for pos in poss]
    return len(poss) / (time.time() - start)


def bench_numpy(lines, kdtree, x, poss, max_dist):
    skymask.np = np
    start = time.time()
    res = []
    for pos in poss:
        selected_lines, selected = select_lines(
            x, lines, kdtree, pos=pos, max_dist=max_dist
        )
        a1, a2 = calc_alpha(x, selected_lines, selected)
        res.append(np.pi / 2 - np.concatenate((a1, a2), axis=0))
    return len(poss) / (time.time() - start)


def bench_cupy(lines, kdtree, x, poss, max_dist):
    skymask.np = cp
    x, lines = cp.asarray(x), cp.asarray(lines)
    start = time.time()
    res = []
    for pos in poss:
        selected_lines, selected = select_lines(
            x, lines, kdtree, pos=pos, max_dist=max_dist
        )
        a1, a2 = calc_alpha(x, selected_lines, selected)
        res.append((cp.pi / 2 - cp.concatenate((a1, a2), axis=0)).get())
    return len(poss) / (time.time() - start)


if __name__ == "__main__":
    num_samples = 1000
    num_pos = 1000
    max_dist = 1000.0
    eps = 1e-6
    pos0 = [500051.31195, 3458536.803]
    poss = [[j + i * 0.5 for j in pos0] for i in range(num_pos)]

    x = np.linspace(-np.pi, np.pi, num=num_samples, endpoint=False)
    world = skymask_py.World(
        "./local/Shanghai/Shanghai_Buildings_DWG-Polygon.shp", max_dist, eps
    )
    lines = world.lines
    kdtree = build_kdtree(
        np.vstack((lines[:, (0, 3)].mean(axis=1), lines[:, (1, 4)].mean(axis=1))).T
    )
    x2 = np.linspace(0, np.pi, num=num_samples // 2, endpoint=False)

    print("Rust parallel:", bench_rust_par(world, poss, x))
    print("Rust:", bench_rust(world, poss, x))
    print("Cupy:", bench_cupy(lines, kdtree, x2, poss, max_dist))
    print("Numpy:", bench_numpy(lines, kdtree, x2, poss, max_dist))
