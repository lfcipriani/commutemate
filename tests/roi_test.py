from nose.tools import *
from commutemate.detectors import *
from commutemate.gpx_parser import GpxParser
from commutemate.roi import PointOfInterest, RegionOfInterest

class TestPOI:

    def test_poi_json_serialization(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stop_POIs, ignored_time = detect_stops(ride)
        js = stop_POIs[2].to_JSON()
        stop_POI = PointOfInterest.from_JSON(js)

        eq_(stop_POI.duration, 19)
        eq_(stop_POI.previous_stop, 'e341decc40fa755c4a1f40792052fcb8')
        eq_(stop_POI.previous_stop_ROI, None)
        eq_(stop_POI.previous_pass_ROI, None)
        eq_(stop_POI.poi_type, PointOfInterest.TYPE_STOP)

class TestROI:

    def test_is_poi_included(self):
        roi = RegionOfInterest()
        poi_ids_stop = ['06dd1e03b5684f3e763c1f006c53d032','6ddc358f6040f3a4be348c5ea7fa398c','6e0d4fb291cc4e6f5c5d40e8471710cc']
        poi_ids_pass = ['6e9ecd248699c93b3e52df56396b0103']
        roi.set_poi_ids(poi_ids_stop, PointOfInterest.TYPE_STOP)
        roi.set_poi_ids(poi_ids_pass, PointOfInterest.TYPE_PASS)

        ok_(roi.is_poi_included("06dd1e03b5684f3e763c1f006c53d032"))
        ok_(not roi.is_poi_included("non_existent_id"))

    def test_ROI_hydration(self):
        roi = RegionOfInterest()
        poi_ids_stop = ['06dd1e03b5684f3e763c1f006c53d032','6ddc358f6040f3a4be348c5ea7fa398c','6e0d4fb291cc4e6f5c5d40e8471710cc']
        poi_ids_pass = ['6e9ecd248699c93b3e52df56396b0103']
        roi.set_poi_ids(poi_ids_stop, PointOfInterest.TYPE_STOP)
        roi.set_poi_ids(poi_ids_pass, PointOfInterest.TYPE_PASS)

        ok_(not roi.center_range)
        ok_(not roi.poi_list[PointOfInterest.TYPE_STOP])
        
        RegionOfInterest.hydrate_POIs(roi, 'tests/data/')
        roi.calculate_center_range(2500)

        eq_(int(roi.center_range[2]), 2500)
        eq_(type(roi.poi_list[PointOfInterest.TYPE_STOP][0]), PointOfInterest)
        eq_(len(roi.poi_list[PointOfInterest.TYPE_STOP]), 3)
        eq_(len(roi.poi_list[PointOfInterest.TYPE_PASS]), 1)
        eq_(len(roi.poi_coords[PointOfInterest.TYPE_STOP]), 3)
        eq_(len(roi.poi_coords[PointOfInterest.TYPE_PASS]), 1)

    def test_roi_json_serialization(self):
        roi = RegionOfInterest()
        poi_ids_stop = ['06dd1e03b5684f3e763c1f006c53d032','6ddc358f6040f3a4be348c5ea7fa398c','6e0d4fb291cc4e6f5c5d40e8471710cc']
        poi_ids_pass = ['6e9ecd248699c93b3e52df56396b0103']
        roi.set_poi_ids(poi_ids_stop, PointOfInterest.TYPE_STOP)
        roi.set_poi_ids(poi_ids_pass, PointOfInterest.TYPE_PASS)
        RegionOfInterest.hydrate_POIs(roi, 'tests/data/')
        roi.calculate_center_range()

        js = roi.to_JSON()
        new_roi = RegionOfInterest.from_JSON(js)

        eq_(int(new_roi.center_range[2]), 2380)
        ok_(not new_roi.poi_list[PointOfInterest.TYPE_STOP])

        RegionOfInterest.hydrate_POIs(new_roi, 'tests/data/')

        eq_(int(new_roi.center_range[2]), 2380)
        eq_(type(new_roi.poi_list[PointOfInterest.TYPE_STOP][0]), PointOfInterest)
        eq_(len(new_roi.poi_list[PointOfInterest.TYPE_STOP]), 3)
        eq_(len(new_roi.poi_list[PointOfInterest.TYPE_PASS]), 1)
        eq_(len(new_roi.poi_coords[PointOfInterest.TYPE_STOP]), 3)
        eq_(len(new_roi.poi_coords[PointOfInterest.TYPE_PASS]), 1)

