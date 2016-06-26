from nose.tools import *
from commutemate.geo_point import GeoPoint

class TestGeoPoint:

    def test_geo_point_constructor(self):
        p = GeoPoint(1,2,10)
        eq_(p.lat, 1)

    def test_available_attributes(self):
        p = GeoPoint(1,2,10,18)
        eq_(p.lat, 1)
        eq_(p.lon, 2)
        eq_(p.altitude, 10)
        eq_(p.speed, 18)

