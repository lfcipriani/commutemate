from nose.tools import *
import os
from commutemate.gpx_parser import GpxParser
from commutemate.ride import GeoPoint
import commutemate.utils as utils

class TestUtils:

    def test_geo_distance(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        p1 = ride.points[42]
        p2 = ride.points[43]

        eq_(int(utils.geo_distance(p1, p2)),6)

    def test_geo_speed(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        p1 = ride.points[42]
        p2 = ride.points[43]
        timedelta = p2.time - p1.time
        distance = utils.geo_distance(p2, p1)

        eq_(int(utils.geo_speed(distance, timedelta)),22)

    def test_full_path(self):
        cwd = os.getcwd()
        eq_(utils.full_path("testing/this/method.gpx"), cwd + "/testing/this/method.gpx")

    def test_load_save_JSON(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        p1 = ride.points[42]
        filename = 'tests/data/test.json'
        utils.save_json(filename, p1.to_JSON())

        ok_(os.path.exists(filename))

        js = utils.load_json(filename, GeoPoint)
        eq_(js.lat, p1.lat)

        os.remove(filename)
        ok_(not os.path.exists(filename))

