#!/usr/bin/env python3

import datetime, pytz, geojson, model, os
from housepy import config, log, server, util, process

process.secure_pid(os.path.join(os.path.dirname(__file__), "run"))

class Home(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("map2.html")

class Beta(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("map3.html")

class Images(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("images.html")

class HeartRate(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("heartrate.html")

class Api(server.Handler):
    
    def get(self, page=None):
        if not len(page):
            return self.render("api.html")    
        if page == "timeline":
            return self.get_timeline()
        return self.not_found()

    def get_timeline(self):
        kinds = self.get_argument('types', "beacon").split(',')
        kinds = [kind.rstrip('s') for kind in kinds if kind.rstrip('s') in ['ambit', 'ambit_geo', 'sighting', 'breadcrumb', 'image', 'audio', 'breadcrumb', 'beacon']]   # sanitizes
        try:
            dt = self.get_argument('date', datetime.datetime.now(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%d"))
            log.debug(dt)
            dt = util.parse_date(dt, tz=config['local_tz'])
            days = int(self.get_argument('days', 1))
        except Exception as e:
            return self.error("Bad parameters: %s" % log.exc(e))
        t = util.timestamp(dt)        
        log.debug("--> search for kinds: %s" % kinds)
        features = model.fetch_features(kinds, t, t + (days * (24 * 60 * 60)))
        feature_collection = geojson.FeatureCollection(features)
        return self.json(feature_collection)


handlers = [
    (r"/api/?([^/]*)", Api),
    (r"/?([^/]*)", Home),
    (r"/images/?([^/]*)", Images),
    (r"/heartrate/?([^/]*)", HeartRate),
    (r"/beta/?([^/]*)", Beta),
]    

server.start(handlers)
