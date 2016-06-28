from nose.tools import *
from commutemate.detectors import *
from commutemate.gpx_parser import GpxParser
from commutemate.roi import PointOfInterest

class TestDetectors:

    def test_detect_stops(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stop_POIs = detect_stops(ride)

        eq_(len(stop_POIs),4)
        eq_(stop_POIs[0].type, PointOfInterest.TYPE_STOP)
        eq_(stop_POIs[0].previous_stop, None)
        eq_(stop_POIs[1].previous_stop.duration, stop_POIs[0].duration)
        eq_(stop_POIs[2].origin, ride.origin)

