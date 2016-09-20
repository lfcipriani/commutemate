from nose.tools import *
from commutemate.config import *

class TestConfig:

    def test_loading_config(self):
        c = Config('tests/data/config_test.ini')

        eq_(len(c.region_ignores), 2)

    def test_fetching_attributes(self):
        c = Config('tests/data/config_test.ini')

        eq_(len(c.region_ignores), 2)
        eq_(c.region_ignores[0][0], -21.790300)
        eq_(c.region_ignores[1][2], 200)
        eq_(c.dbscan_eps_in_meters, 7)
        eq_(c.dbscan_min_samples, 4)
        eq_(c.stops_cap_durations_at, 120)

    def test_empty_region_ignores(self):
        c = Config('tests/data/config_test_no_ignore.ini')

        eq_(len(c.region_ignores), 0)

    def test_empty_stops_cap_duration_at(self):
        c = Config('tests/data/config_test_no_ignore.ini')

        eq_(c.stops_cap_durations_at, None)

    def test_default_config(self):
        c = Config()

        eq_(len(c.region_ignores), 0)
        eq_(c.dbscan_eps_in_meters, 7)
        eq_(c.dbscan_min_samples, 4)
        eq_(c.stops_cap_durations_at, None)
