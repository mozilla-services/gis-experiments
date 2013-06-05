import random
from collections import defaultdict
from math import sqrt
import matplotlib
from matplotlib import pyplot, colors
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from shapely.geometry import Point, MultiPoint
from descartes.patch import PolygonPatch


DB = {}
DEVICES = defaultdict(list)


def guess_location(asus):
    # find the places in our DB
    # for each device we have crowdsourced locations
    # we want to pick the ones where the asu is the closest
    picked = defaultdict(int)

    for asu in asus:
        id = asu['id']
        asu = asu['asu']

        if id in DEVICES:
            current_delta = -1
            current_location = None

            for location, location_asu in DEVICES[id]:
                delta = abs(location_asu - asu)
                if delta < current_delta or current_delta == -1:
                    current_delta = delta
                    current_location = location

            picked[current_location] += 1

    # we've picked some locations, let's return the one
    # that has the most occurrences
    sorting = [(occurence, location) for location, occurence in picked.items()]
    sorting.sort()
    return sorting[0][1]


class Map(object):
    def __init__(self):
        self.fig = pyplot.figure(1, figsize=(10, 10), dpi=90)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self._picked = []

    def plot_coords(self, lon=0, lat=0, color=None, char='o', size=12, id=''):
        if color is None:
            color = random.choice(colors.cnames.values())
            while color in self._picked:
                color = random.choice(colors.cnames.values())
            self._picked.append(color)

        self.ax.plot(lon, lat, char, color=color, zorder=1, label=id,
                     markersize=size)

    def _draw_legend(self):
        handles, labels = self.ax.get_legend_handles_labels()
        self.ax.legend(handles[::-1], labels[::-1])
        handles2 = []
        labels2 = []

        for handle, label in zip(handles, labels):
            if 'wifi' in label:
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


def get_asu(loc1, loc2):
    # distance
    x1, y1 = loc1
    x2, y2 = loc2
    dist = abs(sqrt((x2 - x1)**2 + (y2 - y1)**2))
    dist *= 20

    if dist > 100:
        dist = 100
    return 100 - dist


map = Map()
# here's the reality: a place with one cell tower and 5 wifis
reality = [
        {'id': 'cell tower', 'lon': 43.2, 'lat': 2.2, 'char': '^', 'size': 15},
        {'id': 'wifi1', 'lon': 43.1, 'lat': 1.9},
        {'id': 'wifi2', 'lon': 42.8, 'lat': 2.7},
        {'id': 'wifi3', 'lon': 43.9, 'lat': 2.2},
        {'id': 'wifi4', 'lon': 42.2, 'lat': 1.2},
        {'id': 'wifi5', 'lon': 42.0, 'lat': 2.9}
]

for location in reality:
    map.plot_coords(**location)


# now bob is walking around, and knows his location by GPS, so he can
# crowd-source it. For each device he sees, he is sending back
# its id and asu
bob = {'id': 'bob', 'lon': 41.9, 'lat': 2.3, 'size': 20, 'char': 'v'}
map.plot_coords(**bob)

bob_location = bob['lon'], bob['lat']

asus = []
for device in reality:
    device_location = location['lon'], location['lat']
    asu = get_asu(bob_location, device_location)
    asus.append({'id': location['id'],
                 'asu': asu})
    DEVICES[location['id']].append((bob_location, asu))

DB[bob_location] = asus


# now sarah is hanging around the same area, she does not know
# her location but she sees the same devices around her.

# her location is  41.9, 2.0 but we want our system to find it
sarah = {'id': 'sarah', 'lon': 43.9, 'lat': 2.3, 'size': 20, 'char': '>'}
map.plot_coords(**sarah)

# she's sending the asus she sees
asus2 = []

for device in reality:
    device_location = device['lon'], device['lat']
    asus2.append({'id': location['id'],
                 'asu': get_asu(bob_location, device_location)})


guessed_lon, guessed_lat = guess_location(asus2)
guessed_sarah = {'id': 'sarah (guessed)',
                 'lon': guessed_lon, 'lat': guessed_lat, 'size': 20, 'char': '<'}
map.plot_coords(**guessed_sarah)

map.show()

