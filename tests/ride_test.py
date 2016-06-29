from nose.tools import *
from datetime import datetime
from commutemate.ride import *

class TestGeoPoint:

    def test_geo_point_constructor(self):
        p = GeoPoint(1,2,10,18,2,datetime.today())
        eq_(p.lat, 1)

    def test_available_attributes(self):
        today = datetime.today()
        p = GeoPoint(1,2,10,18,2,today)
        eq_(p.lat, 1)
        eq_(p.lon, 2)
        eq_(p.elevation, 10)
        eq_(p.speed, 18)
        eq_(p.seconds_from_previous, 2)
        eq_(p.time, today)

    def test_geo_point_json_serialization(self):
        today = datetime(2016,04,20,12,13,14)
        p1 = GeoPoint(1,2,10,18.123,2,today)
        js = p1.to_JSON()
        p2 = GeoPoint.from_JSON(js)

        eq_(p2.lat, 1)
        eq_(p2.lon, 2)
        eq_(p2.elevation, 10)
        eq_(p2.speed, 18.123)
        eq_(p2.seconds_from_previous, 2)
        eq_(p2.time, today)

class TestRide:

    def test_add_point(self):
        p = GeoPoint(1,2,10,18,2,datetime.today())
        r = Ride()

        eq_(r.point_count(), 0)
        r.add_point(p)
        eq_(r.point_count(), 1)

    @raises(RideError)
    def test_add_invalid_point(self):
        p = (1,2,10)
        r = Ride()

        r.add_point(p)

    def test_set_origin_and_destination(self):
        origin      = GeoPoint(1,2,10,18,2,datetime.today())
        destination = GeoPoint(3,4,10,18,2,datetime.today())
        r = Ride()
        r.set_origin(origin)
        r.set_destination(destination)

        eq_(r.origin.lat, 1)
        eq_(r.destination.lat, 3)

    def test_set_origin_and_destination_on_the_constructor(self):
        origin      = GeoPoint(1,2,10,18,2,datetime.today())
        destination = GeoPoint(3,4,10,18,2,datetime.today())
        r = Ride(origin, destination)

        eq_(r.origin.lat, 1)
        eq_(r.destination.lat, 3)
        
    def test_ride_json_serialization(self):
        origin      = GeoPoint(1,2,10,18,2,datetime.today())
        destination = GeoPoint(3,4,10,18,2,datetime.today())
        r = Ride(origin, destination)
        r.add_point(origin)
        r.add_point(destination)
        js = r.to_JSON()
        r1 = Ride.from_JSON(js)

        eq_(r1.origin.lat, 1)
        eq_(r1.destination.lat, 3)
        eq_(r1.point_count(), 2)
