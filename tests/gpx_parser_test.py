from nose.tools import *
from commutemate.gpx_parser import GpxParser

class TestGpxParser:

    def test_loading_gpx_file(self):
        gp = GpxParser('tests/data/sample_with_stop.gpx')
        ok_(isinstance(gp,GpxParser))

    @raises(IOError)
    def test_loading_non_existent_gpx_file(self):
        gp = GpxParser('tests/data/nonexistent.gpx')
