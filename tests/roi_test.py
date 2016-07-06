from nose.tools import *
from commutemate.detectors import *
from commutemate.gpx_parser import GpxParser
from commutemate.roi import PointOfInterest, RegionOfInterest

class TestPOI:

    def test_average_speed_since_previous(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stop_POIs = detect_stops(ride)

        eq_(int(stop_POIs[2].speed_since_previous_stop), 18)
        eq_(stop_POIs[2].duration, 19)
        eq_(stop_POIs[2].previous_stop, 'ce41ef2b46075724919fa8b6579dd144')
        eq_(stop_POIs[2].poi_type, PointOfInterest.TYPE_STOP)

    def test_poi_json_serialization(self):
        ride = GpxParser('tests/data/sample_with_stop.gpx').get_ride_from_track()
        stop_POIs = detect_stops(ride)
        js = stop_POIs[2].to_JSON()
        stop_POI = PointOfInterest.from_JSON(js)

        eq_(int(stop_POI.speed_since_previous_stop), 18)
        eq_(stop_POI.duration, 19)
        eq_(stop_POI.previous_stop, 'ce41ef2b46075724919fa8b6579dd144')
        eq_(stop_POI.poi_type, PointOfInterest.TYPE_STOP)

class TestROI:

    def test_ROI_hydration(self):
        roi = RegionOfInterest()
        poi_ids_core = ['1edf2a64bf9973b4bd774c8f4d073895','1edd013cf467235ad09288c37c07190f','1ec75e917573fbc0896a7082f514209f']
        poi_ids_non_core = ['1ead3fd8056b691e1653c888e29e8e7d']
        roi.set_poi_ids(poi_ids_core, RegionOfInterest.CORE)
        roi.set_poi_ids(poi_ids_non_core, RegionOfInterest.NON_CORE)

        ok_(not roi.center_range)
        ok_(not roi.poi_list[RegionOfInterest.CORE])
        
        RegionOfInterest.hydrate_POIs(roi, 'tests/data/')

        eq_(int(roi.center_range[2]), 1761)
        eq_(type(roi.poi_list[RegionOfInterest.CORE][0]), PointOfInterest)
        eq_(len(roi.poi_list[RegionOfInterest.CORE]), 3)
        eq_(len(roi.poi_list[RegionOfInterest.NON_CORE]), 1)
        eq_(len(roi.poi_coords[RegionOfInterest.CORE]), 3)
        eq_(len(roi.poi_coords[RegionOfInterest.NON_CORE]), 1)

    def test_roi_json_serialization(self):
        roi = RegionOfInterest()
        poi_ids_core = ['1edf2a64bf9973b4bd774c8f4d073895','1edd013cf467235ad09288c37c07190f','1ec75e917573fbc0896a7082f514209f']
        poi_ids_non_core = ['1ead3fd8056b691e1653c888e29e8e7d']
        roi.set_poi_ids(poi_ids_core, RegionOfInterest.CORE)
        roi.set_poi_ids(poi_ids_non_core, RegionOfInterest.NON_CORE)
        RegionOfInterest.hydrate_POIs(roi, 'tests/data/')

        js = roi.to_JSON()
        new_roi = RegionOfInterest.from_JSON(js)

        eq_(int(new_roi.center_range[2]), 1761)
        ok_(not new_roi.poi_list[RegionOfInterest.CORE])

        RegionOfInterest.hydrate_POIs(new_roi, 'tests/data/')

        eq_(int(new_roi.center_range[2]), 1761)
        eq_(type(new_roi.poi_list[RegionOfInterest.CORE][0]), PointOfInterest)
        eq_(len(new_roi.poi_list[RegionOfInterest.CORE]), 3)
        eq_(len(new_roi.poi_list[RegionOfInterest.NON_CORE]), 1)
        eq_(len(new_roi.poi_coords[RegionOfInterest.CORE]), 3)
        eq_(len(new_roi.poi_coords[RegionOfInterest.NON_CORE]), 1)
