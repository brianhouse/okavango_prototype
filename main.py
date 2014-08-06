#!/usr/bin/env python3

import datetime, pytz, geojson, model, os, uuid
from housepy import config, log, server, util, process

process.secure_pid(os.path.abspath(os.path.join(os.path.dirname(__file__), "run")))

__UPLOADS__ = "uploads/"

class Home(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("map3.html")

class Beta(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("map4.html")

class Images(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("images.html")

class Audio(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("audio.html")

class HeartRate(server.Handler):

    def get(self, page=None):
        if len(page):
            return self.not_found()
        return self.render("heartrate.html")

class Userform(server.Handler):
    def get(self):
        self.render("fileuploadform.html")
 
 
class Upload(server.Handler):
    print("UPLOAD REQUESTED.")
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = fname #str(uuid.uuid4()) + extn
        body = self.request.data
        fh = open(__UPLOADS__ + cname, 'w')
        fh.write(bytes(body, 'utf8'))
        self.finish(cname + " is uploaded!! Check %s folder" %__UPLOADS__)

class Api(server.Handler):
    
    def get(self, page=None):
        if not len(page):
            return self.render("api.html")    
        if page == "timeline":
            return self.get_timeline()
        return self.not_found()

    def get_timeline(self):
        skip = self.get_argument('skip', 1)
        kinds = self.get_argument('types', "beacon").split(',')
        kinds = [kind.rstrip('s') for kind in kinds if kind.rstrip('s') in ['ambit', 'ambit_geo', 'sighting', 'breadcrumb', 'image', 'audio', 'breadcrumb', 'beacon', 'heart_spike', 'tweet']]   # sanitizes
        try:
            dt = self.get_argument('date', datetime.datetime.now(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%d"))
            log.debug(dt)
            dt = util.parse_date(dt, tz=config['local_tz'])
            days = int(self.get_argument('days', 1))
        except Exception as e:
            return self.error("Bad parameters: %s" % log.exc(e))
        t = util.timestamp(dt)        
        log.debug("--> !!!! search for kinds: %s" % kinds)
        features = model.fetch_features(kinds, t, t + (days * (24 * 60 * 60)), skip)
        feature_collection = geojson.FeatureCollection(features)
        return self.json(feature_collection)


handlers = [
    (r"/api/?([^/]*)", Api),
    (r"/upload", Upload),
    (r"/uploadform", Userform),
    (r"/images/?([^/]*)", Images),
    (r"/audio/?([^/]*)", Audio),
    (r"/heartrate/?([^/]*)", HeartRate),
    (r"/beta/?([^/]*)", Beta),
    (r"/?([^/]*)", Home),    
]    

server.start(handlers)
print("Okavango server starter. Version 1.1")
