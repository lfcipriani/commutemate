import gpxpy

class GpxParser(object):

    def __init__(self, filename):
        gpx_file = open(filename, 'r')
        self.__gpx = gpxpy.parse(gpx_file)


