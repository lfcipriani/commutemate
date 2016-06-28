from nose.tools import *
from commutemate.detectors import *
from commutemate.gpx_parser import GpxParser
from commutemate.roi import PointOfInterest

class TestPOI:

    def test_average_speed_since_previous(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stop_POIs = detect_stops(ride)

        eq_(int(stop_POIs[2].speed_since_previous_stop), 18)
