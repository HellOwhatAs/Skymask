import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backend_bases import KeyEvent
from matplotlib.figure import Figure
from skymask import np, select_lines, calc_alpha, Tuple, KDTree


class Visualizer:
    def __init__(
        self,
        fig: Figure,
        ax: Axes,
        lines: np.ndarray,
        kdtree: KDTree,
        theta: np.ndarray,
        pos: Tuple[float, float],
        dx: float = 0.1,
        max_dist = np.inf
    ):
        self.fig = fig
        self.ax = ax
        self.lines = lines
        self.kdtree = kdtree
        self.theta = theta
        self.pos = list(pos)
        self.dx = dx
        self.max_dist = max_dist
        self.update()

    def update(self):
        self.ax.yaxis.set_major_formatter("")
        self.ax.set_ylim(0, np.pi / 2)
        self.ax.set_title(f"pos: {self.pos}")

        selected_lines, selected = select_lines(self.theta, self.lines, self.kdtree, pos=self.pos, max_dist=self.max_dist)
        a1, a2 = calc_alpha(self.theta, selected_lines, selected)
        x = np.concatenate(
            (self.theta, (self.theta - np.pi), np.array([self.theta[0]])), axis=0
        )
        y = np.concatenate(
            (np.pi / 2 - a1, np.pi / 2 - a2, np.array([np.pi / 2 - a1[0]])), axis=0
        )
        if np.__name__ == "cupy":
            x, y = x.get(), y.get()
        self.ax.plot(x, y)
        self.ax.fill_between(x, y, np.pi / 2, alpha=0.2)

    def on_press(self, event: KeyEvent):
        if event.key == "up":
            self.pos[1] = round(self.pos[1] + self.dx, 3)
        elif event.key == "left":
            self.pos[0] = round(self.pos[0] - self.dx, 3)
        elif event.key == "down":
            self.pos[1] = round(self.pos[1] - self.dx, 3)
        elif event.key == "right":
            self.pos[0] = round(self.pos[0] + self.dx, 3)
        else:
            return
        self.ax.cla()
        self.update()
        self.fig.canvas.draw()


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
    theta = np.linspace(0, np.pi, num=100, endpoint=False)

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    vis = Visualizer(fig, ax, lines, kdtree, theta, (0, 0))
    fig.canvas.mpl_connect('key_press_event', vis.on_press)
    plt.show()