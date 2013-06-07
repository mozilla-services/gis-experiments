Location demo
=============

Terms
-----

- A signal source (SS) is either a cell tower or a wifi access point

- The location db contains coordinates of cell towers or wifi access points

- a measure is a list of wifi or cell tower, each one with a signal strength
  when possible and a unique key.

- Signal strength is generally some ASU (arbitrary strength unit) measure like
  "16" or "92" with a meaning dependent on the network standard

- Time of flight is a measure of how much time it took a signal to reach the
  user equipment, gathered from things like "round trip time" or "timing advance"

- A cell/wifi record consists of a unique id, a lat/lon location, a network
  standard, a maximum radius, a minimum and maximum signal strength and a maximum
  time of flight

The theory
----------

To build the location db of signal sources, we proceed as following:

1/ a phone device that knows its location collects all signal sources
   it sees around, with an asu for each.

2/ a signal source that has been seen from three different locations
   can have its location guessed using a
   `trilateration <https://en.wikipedia.org/wiki/Trilateration>`_.

3/ when a phone ask for its location, given what it sees around it,
   we can guess it by doing a trilateration based on the signal sources
   it sees.

4/ th location db are constantly refined with new incoming data.


Demo
----

To install and run the demo ::

    $ make build
    $ bin/python demo.py

