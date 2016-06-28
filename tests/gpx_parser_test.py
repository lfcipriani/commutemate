from nose.tools import *
from commutemate.gpx_parser import GpxParser

class TestGpxParser:

    def test_loading_gpx_file(self):
        gp = GpxParser('tests/data/sample_with_stop.gpx')
        ok_(isinstance(gp,GpxParser))

    @raises(IOError)
    def test_loading_non_existent_gpx_file(self):
        gp = GpxParser('tests/data/nonexistent.gpx')

    def test_get_ride_from_track(self):
        gp = GpxParser('tests/data/sample_with_stop.gpx')
        ride = gp.get_ride_from_track()

        eq_(ride.point_count(), 292)
        ok_(ride.points[34].speed > 0)
        ok_(ride.points[34].seconds_from_previous > 0)
        ok_(ride.points[0].speed == 0)
        ok_(ride.points[0].seconds_from_previous == 0)
    
