import random

from matplotlib import pyplot, colors
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from shapely.geometry import Point, MultiPoint
from descartes.patch import PolygonPatch


class Map(object):
    def __init__(self):
        self.fig = pyplot.figure(1, figsize=(10, 10), dpi=90)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self._picked = []

    def plot_coords(self, x=0, y=0, color=None, char='o', size=12, id=''):
        if color is None:
            color = random.choice(colors.cnames.values())
            while color in self._picked:
                color = random.choice(colors.cnames.values())
            self._picked.append(color)

        self.ax.plot(x, y, char, color=color, zorder=1, label=id,
                     markersize=size)

    def _draw_legend(self):
        handles, labels = self.ax.get_legend_handles_labels()
        self.ax.legend(handles[::-1], labels[::-1])
        handles2 = []
        labels2 = []

        for handle, label in zip(handles, labels):
            if 'wifi' in label or label in ('bill', 'bob', 'jon'):
                continue
            handles2.append(handle)
            labels2.append(label)

        self.ax.legend(handles2, labels2, loc=3)

    def show(self):
        self._draw_legend()
        try:
            pyplot.show()
        except KeyboardInterrupt:
            pass
