from nose.tools import *
from commutemate.detectors import *
from commutemate.gpx_parser import GpxParser

class TestDetectors:

    def test_detect_stops(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stops = detect_stops(ride)

        eq_(len(stops),4)

