from utils import trilaterate, lla_distance


class Device(object):

    def __init__(self, id):
        self.id = id
        self.measures = []
        self.x, self.y = None, None


class Devices(object):

    def __init__(self):
        self._locations = {}

    def crowd_source(self, location, neighbours):
        for device in neighbours:
            device_location = device['x'], device['y']
            device_id = device['id']
            asu = lla_distance(location, device_location)

            if device_id in self._locations:
                dbdevice = self._locations[device_id]
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
                    x, y, __ = trilaterate(
                        [loc1, loc2, loc3], [dist1, dist2, dist3])
                except ValueError:
                    print 'cannot trilaterate %s' % dbdevice.id
                else:
                    dbdevice.x, dbdevice.y = x, y
                    print '%s is at %.4f, %.4f' % (dbdevice.id, dbdevice.x,
                                                   dbdevice.y)

            self._locations[device_id] = dbdevice

    def guess_location(self, asus):
        # find the places in our DB
        # for each device we have crowdsourced locations
        # we want to pick the ones where the asu is the closest
        picked = []

        for asu in asus:
            id = asu['id']
            asu = asu['asu']

            if id in self._locations:
                device = self._locations[id]
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
