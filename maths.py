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


class Device(object):
    def __init__(self, id):
        self.id = id
        self.measures = []
        self.lon, self.lat = None, None



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
            if device.lon is not None:
                picked.append((asu, device))

    if len(picked) < 3:
        raise ValueError('nope')

    picked.sort()
    picked.reverse()

    dist1, device1 = picked[0]
    dist2, device2 = picked[1]
    dist3, device3 = picked[2]
    loc1 = device1.lon, device1.lat
    loc2 = device2.lon, device2.lat
    loc3 = device3.lon, device3.lat
    return triangulation(loc1, dist1, loc2, dist2, loc3, dist3)


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


def triangulation(loc1, dist1, loc2, dist2, loc3, dist3):
    LatA, LonA = loc1
    LatB, LonB = loc2
    LatC, LonC = loc3
    # assuming elevation = 0
    earthR = 6371

    #using authalic sphere
    #if using an ellipsoid this step is slightly different
    #Convert geodetic Lat/Long to ECEF xyz
    #   1. Convert Lat/Long to radians
    #   2. Convert Lat/Long(radians) to ECEF
    xA = earthR *(math.cos(math.radians(LatA)) * math.cos(math.radians(LonA)))
    yA = earthR *(math.cos(math.radians(LatA)) * math.sin(math.radians(LonA)))
    zA = earthR *(math.sin(math.radians(LatA)))

    xB = earthR *(math.cos(math.radians(LatB)) * math.cos(math.radians(LonB)))
    yB = earthR *(math.cos(math.radians(LatB)) * math.sin(math.radians(LonB)))
    zB = earthR *(math.sin(math.radians(LatB)))

    xC = earthR *(math.cos(math.radians(LatC)) * math.cos(math.radians(LonC)))
    yC = earthR *(math.cos(math.radians(LatC)) * math.sin(math.radians(LonC)))
    zC = earthR *(math.sin(math.radians(LatC)))

    P1 = array([xA, yA, zA])
    P2 = array([xB, yB, zB])
    P3 = array([xC, yC, zC])

    #from wikipedia
    #transform to get circle 1 at origin
    #transform to get circle 2 on x axis
    ex = (P2 - P1)/(numpy.linalg.norm(P2 - P1))
    i = dot(ex, P3 - P1)
    ey = (P3 - P1 - i*ex)/(numpy.linalg.norm(P3 - P1 - i*ex))
    ez = numpy.cross(ex,ey)
    d = numpy.linalg.norm(P2 - P1)
    j = dot(ey, P3 - P1)

    #from wikipedia
    #plug and chug using above values
    x = (pow(dist1,2) - pow(dist2,2) + pow(d,2))/(2*d)
    y = ((pow(dist1,2) - pow(dist3,2) + pow(i,2) + pow(j,2))/(2*j)) - ((i/j)*x)

    # only one case shown here
    # XXX
    ###z = sqrt(pow(dist1,2) - pow(x,2) - pow(y,2))
    z = sqrt(abs(pow(dist1,2) - pow(x,2) - pow(y,2)))

    #triPt is an array with ECEF x,y,z of trilateration point
    triPt = P1 + x*ex + y*ey + z*ez

    #convert back to lat/long from ECEF
    #convert to degrees
    lat = math.degrees(math.asin(triPt[2] / earthR))
    lon = math.degrees(math.atan2(triPt[1],triPt[0]))

    return lat, lon


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


def crowd_source(location):
    asus = []
    for device in reality:
        device_location = device['lon'], device['lat']
        device_id = device['id']
        asu = get_asu(location, device_location)

        if device_id in DEVICES:
            device = DEVICES[device_id]
        else:
            device = Device(device_id)

        # see how to ignore / drop
        device.measures.append((location, asu))

        # do we have 3 measures ?
        if len(device.measures) > 2 and device.lon is None:
            loc1, ss1 = device.measures[0]
            loc2, ss2 = device.measures[1]
            loc3, ss3 = device.measures[2]
            lon, lat =  triangulation(loc1, ss1, loc2, ss2, loc3, ss3)
            device.lon, device.lat = lon, lat

        DEVICES[device_id] = device

# now bob is walking around, and knows his location by GPS, so he can
# crowd-source it. For each device he sees, he is sending back
# its id and asu
bob = {'id': 'bob', 'lon': 41.9, 'lat': 2.3, 'size': 20, 'char': 'v'}
map.plot_coords(**bob)

bob_location = bob['lon'], bob['lat']
crowd_source(bob_location)



# jon does the same thing
jon = {'id': 'jon', 'lon': 40.9, 'lat': 1.3, 'size': 20, 'char': '<'}
map.plot_coords(**jon)
jon_location = jon['lon'], jon['lat']

crowd_source(jon_location)


# then bill
bill = {'id': 'bill', 'lon': 43.9, 'lat': 2.4, 'size': 20, 'char': 'x'}
map.plot_coords(**bill)
bill_location = bill['lon'], bill['lat']
crowd_source(bill_location)

# now sarah is hanging around the same area, she does not know
# her location but she sees the same devices around her.

# her location is  41.9, 2.0 but we want our system to find it
sarah = {'id': 'sarah', 'lon': 43.9, 'lat': 2.3, 'size': 20, 'char': '>'}
map.plot_coords(**sarah)

# she's sending the asus she sees
asus2 = []

for device in reality:
    device_location = device['lon'], device['lat']
    asus2.append({'id': device['id'],
                 'asu': get_asu(bob_location, device_location)})


guessed_lon, guessed_lat = guess_location(asus2)
guessed_sarah = {'id': 'sarah (guessed)',
                 'lon': guessed_lon, 'lat': guessed_lat, 'size': 20, 'char': '<'}
map.plot_coords(**guessed_sarah)

map.show()

