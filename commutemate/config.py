import ConfigParser

class Config(object):

    def __init__(self, filename=None):
        if filename:
            self.filename = filename
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
            self.dbscan_eps_in_meters = float(c.get('dbscan','eps_in_meters'))
            self.dbscan_min_samples   = int(c.get('dbscan','min_samples'))

            try:
                cap_time = int(c.get('stops','cap_durations_at'))
            except ConfigParser.NoOptionError:
                self.stops_cap_durations_at = None
            else:
                self.stops_cap_durations_at = cap_time

        else:
            self.filename = 'default'
            # DEFAULT values
            # region ignores
            self.region_ignores = []
            # dbscan
            self.dbscan_eps_in_meters = 7.
            self.dbscan_min_samples   = 4

            self.stops_cap_durations_at = None

    def __str__(self):
        rg = [reg.__str__() for reg in self.region_ignores]
        return "Config loaded from: %s\n  - regions_ignore: %s\n  - dbscan_eps_in_meters: %d\n  - dbscan_min_samples: %d\n  - stops_cap_durations_at: %s" % (self.filename, ",".join(rg), self.dbscan_eps_in_meters, self.dbscan_min_samples, self.stops_cap_durations_at)

