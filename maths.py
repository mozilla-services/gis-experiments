import random
from collections import defaultdict
from math import sqrt
import matplotlib
from matplotlib import pyplot, colors
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from shapely.geometry import Point, MultiPoint
from descartes.patch import PolygonPatch
from math import *
from numpy import *
import numpy


DB = {}
DEVICES = {}

from utils import trilaterate, lla_distance


class Device(object):
    def __init__(self, id):
        self.id = id
        self.measures = []
        self.x, self.y = None, None



def guess_location(asus):
    # find the places in our DB
    # for each device we have crowdsourced locations
    # we want to pick the ones where the asu is the closest
    picked = []

    for asu in asus:
        id = asu['id']
        asu = asu['asu']

        if id in DEVICES:
            device = DEVICES[id]
            if device.x is not None:
                picked.append((asu, device))

    if len(picked) < 3:
        raise ValueError('nope')

    picked.sort()
    picked.reverse()

    dist1, device1 = picked[0]
    dist2, device2 = picked[1]
    dist3, device3 = picked[2]
    loc1 = device1.x, device1.y
    loc2 = device2.x, device2.y
    loc3 = device3.x, device3.y
    x, y, __ = trilaterate([loc1, loc2, loc3], [dist1, dist2, dist3])
    return x, y


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


map = Map()
# here's the reality: a place with one cell tower and 5 wifis
reality = [
        {'id': 'cell tower',
                        'x': 43.136944, 'y': 2.287623, 'char': '^', 'size': 15},
        {'id': 'wifi1', 'x': 43.132098, 'y': 1.932456},
        {'id': 'wifi2', 'x': 42.809876, 'y': 2.798754},
        {'id': 'wifi3', 'x': 43.209975, 'y': 2.239235},
        {'id': 'wifi4', 'x': 41.932323, 'y': 1.227653},
        {'id': 'wifi5', 'x': 42.023398, 'y': 2.128209}
]

for location in reality:
    map.plot_coords(**location)


def crowd_source(location):
    asus = []
    for device in reality:
        device_location = device['x'], device['y']
        device_id = device['id']
        asu = lla_distance(location, device_location)

        if device_id in DEVICES:
            dbdevice = DEVICES[device_id]
        else:
            dbdevice = Device(device_id)

        # see how to ignore / drop
        dbdevice.measures.append((location, asu))

        # do we have 3 measures ?
        if len(dbdevice.measures) > 2 and dbdevice.x is None:
            loc1, dist1 = dbdevice.measures[0]
            loc2, dist2 = dbdevice.measures[1]
            loc3, dist3 = dbdevice.measures[2]
            try:
                x, y, __ = trilaterate([loc1, loc2, loc3], [dist1, dist2, dist3])
            except ValueError:
                print 'cannot trilaterate %s' % dbdevice.id
            else:
                dbdevice.x, dbdevice.y = x, y
                print '%s is at %.4f, %.4f' % (dbdevice.id, dbdevice.x, dbdevice.y)
        DEVICES[device_id] = dbdevice

# now bob is walking around, and knows his location by GPS, so he can
# crowd-source it. For each device he sees, he is sending back
# its id and asu
bob = {'id': 'bob', 'x': 43.937484, 'y': 2.348756, 'size': 20, 'char': 'v'}
map.plot_coords(**bob)

bob_location = bob['x'], bob['y']
crowd_source(bob_location)



# jon does the same thing
jon = {'id': 'jon', 'x': 42.432546, 'y': 1.333467, 'size': 20, 'char': '<'}
map.plot_coords(**jon)
jon_location = jon['x'], jon['y']
crowd_source(jon_location)


# then bill
bill = {'id': 'bill', 'x': 41.938347, 'y': 1.738475, 'size': 20, 'char': '8'}
map.plot_coords(**bill)
bill_location = bill['x'], bill['y']
crowd_source(bill_location)

# now sarah is hanging around the same area, she does not know
# her location but she sees the same devices around her.

# her location is  40.9, 1.8 but we want our system to find it
sarah = {'id': 'sarah', 'x': 43.904945, 'y': 1.838475, 'size': 20, 'char': '>'}
sarah_location = sarah['x'], sarah['y']
map.plot_coords(**sarah)

# she's sending the asus she sees
asus2 = []

for device in reality:
    device_location = device['x'], device['y']
    asu = lla_distance(sarah_location, device_location)
    asus2.append({'id': device['id'],
                 'asu': asu})


guessed_x, guessed_y = guess_location(asus2)
guessed_sarah = {'id': 'sarah (guessed)',
                 'x': guessed_x, 'y': guessed_y, 'size': 20, 'char': '<'}
map.plot_coords(**guessed_sarah)

print 'Sarah %.4f, %.4f' % (sarah['x'], sarah['y'])
print 'Guess %.4f %.4f' % (guessed_x, guessed_y)


map.show()

