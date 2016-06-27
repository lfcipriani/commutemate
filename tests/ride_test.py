from nose.tools import *
from commutemate.ride import *

class TestGeoPoint:

    def test_geo_point_constructor(self):
        p = GeoPoint(1,2,10,18)
        eq_(p.lat, 1)

    def test_available_attributes(self):
        p = GeoPoint(1,2,10,18)
        eq_(p.lat, 1)
        eq_(p.lon, 2)
        eq_(p.altitude, 10)
        eq_(p.speed, 18)

class TestRide:

    def test_add_point(self):
        p = GeoPoint(1,2,10,18)
        r = Ride()

        eq_(r.point_count(), 0)
        r.add_point(p)
        eq_(r.point_count(), 1)

    @raises(RideError)
    def test_add_invalid_point(self):
        p = (1,2,10)
        r = Ride()

        r.add_point(p)
