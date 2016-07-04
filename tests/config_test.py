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

