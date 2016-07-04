import ConfigParser

class Config(object):

    def __init__(self, filename):
        self.config = ConfigParser.ConfigParser()
        self.config.read(filename)
        c = self.config

        # region ignores
        self.region_ignores = []
        for key, region in c.items('region_ignore'):
            l = region.split(",")
            l[0] = float(l[0])
            l[1] = float(l[1])
            l[2] = int(l[2])
            self.region_ignores.append(l)

        # dbscan
        self.dbscan_eps_in_meters = int(c.get('dbscan','eps_in_meters'))
        self.dbscan_min_samples   = int(c.get('dbscan','min_samples'))

