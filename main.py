#!/usr/bin/env python3

import datetime, pytz, geojson, model, os
from housepy import config, log, server, util, process

process.secure_pid(os.path.join(os.path.dirname(__file__), "run"))

class Home(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("home.html")


class Api(server.Handler):
    
    def get(self, page=None):
        if not len(page):
            return self.render("api.html")    
        if page == "timeline":
            return self.get_timeline()
        return self.not_found()

    def get_timeline(self):
        kinds = self.get_argument('types', "positions").split(',')
        kinds = [kind.rstrip('s') for kind in kinds if kind.rstrip('s') in ['ambit', 'sighting', 'breadcrumb', 'image', 'audio', 'breadcrumb', 'beacon']]   # sanitizes
        dt = self.get_argument('date', datetime.datetime.now(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%d"))
        dt = util.parse_date(dt, tz=config['local_tz'])
        t = util.timestamp(dt)        
        log.debug("--> search for kinds: %s" % kinds)
        features = model.fetch_features(kinds, t, t + (24 * 60 * 60))
        feature_collection = geojson.FeatureCollection(features)
        return self.json(feature_collection)


handlers = [
    (r"/api/?([^/]*)", Api),
    (r"/?([^/]*)", Home),
]    

server.start(handlers)
