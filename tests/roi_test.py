from nose.tools import *
from commutemate.detectors import *
from commutemate.gpx_parser import GpxParser
from commutemate.roi import PointOfInterest

class TestPOI:

    def test_average_speed_since_previous(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stop_POIs = detect_stops(ride)

        eq_(int(stop_POIs[2].speed_since_previous_stop), 18)
        eq_(stop_POIs[2].duration, 19)
        eq_(stop_POIs[2].previous_stop, 736062)
        eq_(stop_POIs[2].poi_type, PointOfInterest.TYPE_STOP)

    def test_poi_json_serialization(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stop_POIs = detect_stops(ride)
        js = stop_POIs[2].to_JSON()
        stop_POI = PointOfInterest.from_JSON(js)

        eq_(int(stop_POI.speed_since_previous_stop), 18)
        eq_(stop_POI.duration, 19)
        eq_(stop_POI.previous_stop, 736062)
        eq_(stop_POI.poi_type, PointOfInterest.TYPE_STOP)
