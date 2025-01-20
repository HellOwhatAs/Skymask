import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backend_bases import KeyEvent
from matplotlib.figure import Figure
from skymask import np, select_lines, calc_alpha, Tuple


class Visualizer:
    def __init__(
        self,
        fig: Figure,
        ax: Axes,
        lines: np.ndarray,
        theta: np.ndarray,
        pos: Tuple[float, float],
    ):
        self.fig = fig
        self.ax = ax
        self.lines = lines
        self.theta = theta
        self.pos = list(pos)
        self.update()

    def update(self):
        self.ax.yaxis.set_major_formatter("")
        self.ax.set_ylim(0, np.pi / 2)
        self.ax.set_title(f"pos: {self.pos}")
        selected_lines, selected = select_lines(self.theta, self.lines, pos=self.pos)
        a1, a2 = calc_alpha(self.theta, selected_lines, selected)
        x = np.concatenate(
            (self.theta, (self.theta - np.pi), np.array([self.theta[0]])), axis=0
        )
        y = np.concatenate(
            (np.pi / 2 - a1, np.pi / 2 - a2, np.array([np.pi / 2 - a1[0]])), axis=0
        )
        self.ax.plot(x, y)
        self.ax.fill_between(x, y, np.pi / 2, alpha=0.2)

    def on_press(self, event: KeyEvent):
        if event.key == "up":
            self.pos[1] = round(self.pos[1] + 0.1, 3)
        elif event.key == "left":
            self.pos[0] = round(self.pos[0] - 0.1, 3)
        elif event.key == "down":
            self.pos[1] = round(self.pos[1] - 0.1, 3)
        elif event.key == "right":
            self.pos[0] = round(self.pos[0] + 0.1, 3)
        else:
            return
        self.ax.cla()
        self.update()
        self.fig.canvas.draw()


if __name__ == "__main__":
    lines = np.array([
        #  xa,   ya,   za,   xb,   yb,  zb
        [ 1.0,  1.0,  1.0, -1.0,  1.0, 1.0],
        [-1.0,  1.0,  1.0, -1.0, -1.0, 1.0],
        [-1.0, -1.0,  1.0,  1.0, -1.0, 1.0],
        [ 1.0, -1.0,  1.0,  1.0,  1.0, 1.0],
    ])
    theta = np.linspace(0, np.pi, num=100, endpoint=False)

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    vis = Visualizer(fig, ax, lines, theta, (0, 0))
    fig.canvas.mpl_connect('key_press_event', vis.on_press)
    plt.show()