from nose.tools import *
import os
from datetime import datetime
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

    def test_is_inside_range(self):
        inside  = GeoPoint(47.558094,10.749937,10,18,2,datetime.today())
        outside = GeoPoint(47.560451,10.748338,10,18,2,datetime.today())
        range_  = (47.557729, 10.750323, 200)

        ok_(utils.is_inside_range(range_, inside))
        ok_(not utils.is_inside_range(range_, outside))

    def test_geo_range_from_center(self):
        points = [[-22.007023, -47.895010],[-22.007600, -47.894592],[-22.007608, -47.895222],[-22.006996, -47.894444],[-22.007264, -47.894572],[-22.007299, -47.894703],[-22.007394, -47.894159],[-22.007615, -47.894285]]
        range_ = utils.geo_range_from_center(points)

        eq_(range_[0],-22.0073055)
        eq_(range_[1],-47.894690499999996)
        eq_(int(range_[2]),54)

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

