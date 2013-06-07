from db import Devices
from map import Map
from utils import lla_distance

devices = Devices()
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


# now bob is walking around, and knows his location by GPS, so he can
# crowd-source it. For each device he sees, he is sending back
# its id and asu
bob = {'id': 'bob', 'x': 43.937484, 'y': 2.348756, 'size': 20, 'char': 'v'}
map.plot_coords(**bob)

bob_location = bob['x'], bob['y']
devices.crowd_source(bob_location, reality)


# jon does the same thing
jon = {'id': 'jon', 'x': 42.432546, 'y': 1.333467, 'size': 20, 'char': '<'}
map.plot_coords(**jon)
jon_location = jon['x'], jon['y']
devices.crowd_source(jon_location, reality)


# then bill
bill = {'id': 'bill', 'x': 41.938347, 'y': 1.738475, 'size': 20, 'char': '8'}
map.plot_coords(**bill)
bill_location = bill['x'], bill['y']
devices.crowd_source(bill_location, reality)

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


guessed_x, guessed_y = devices.guess_location(asus2)
guessed_sarah = {'id': 'sarah (guessed)',
                 'x': guessed_x, 'y': guessed_y, 'size': 20, 'char': '<'}
map.plot_coords(**guessed_sarah)

print 'Sarah %.4f, %.4f' % (sarah['x'], sarah['y'])
print 'Guess %.4f %.4f' % (guessed_x, guessed_y)


map.show()
