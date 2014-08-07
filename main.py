#!/usr/bin/env python3

import datetime, pytz, geojson, model, os, uuid, shutil
from housepy import config, log, server, util, process

process.secure_pid(os.path.abspath(os.path.join(os.path.dirname(__file__), "run")))

__UPLOADS__ = "uploads/"

#2014 ingest via API

def ingest_image_api(path):
    log.info("ingest_image %s" % path)
    date_string = path.split('/')[-1]
    date_string = date_string.split('.')[0]
    log.info("ingest_image %s" % date_string)
    #060814154100
    dt = datetime.datetime.strptime(date_string.split('_')[0], "%d%m%y%H%M%S")
    log.info("datetime %s" % dt)
    tz = pytz.timezone(config['local_tz'])
    dt = tz.localize(dt)
    t = util.timestamp(dt)
    log.info("timestamp %s" % t)

    try:
        image = Image.open(path)
        width, height = image.size    
    except Exception as e:
        log.error(log.exc(e))
        width, height = None, None      

    coords = model.get_coords_by_time(t);
    feature = geojson.Feature(geometry=coords,properties={'utc_t': t, 'ContentType': "image", 'url': "/static/data/images/%s.jpg" % (t), 'DateTime': dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z"), 'size': [width, height]})
    feature_id = model.insert_feature('image', t, geojson.dumps(feature))
    new_path = os.path.join(os.path.dirname(__file__), "static", "data", "images", "%s.jpg" % (t))
    shutil.copy(path, new_path)

def ingest_audio_api(path, i):
    log.info("ingest_audio %s" % path)
    dt = datetime.datetime.strptime(path.split('/')[-1], "audio %d%m%Y_%H%M.mp3")
    tz = pytz.timezone(config['local_tz'])
    dt = tz.localize(dt)
    t = util.timestamp(dt)    
    # if t <= t_protect:
    #     log.warning("Protected t, skipping...")
    #     return    
    fixed_path = path.replace(".mp3", ".amr")
    shutil.move(path, fixed_path)
    new_path = os.path.join(os.path.dirname(__file__), "static", "data", "audio", "%s-%s.wav" % (t, i))    
    try:
        log.debug("--> converting [%s] to [%s]" % (fixed_path, new_path))
        subprocess.check_call("%s -y -i '%s' '%s'" % (config['ffmpeg'], os.path.abspath(fixed_path), os.path.abspath(new_path)), shell=True)
    except Exception as e:
        log.error(log.exc(e))
        return
    feature = geojson.Feature(properties={'utc_t': t, 'ContentType': "audio", 'url': "/static/data/audio/%s-%s.wav" % (t, i), 'DateTime': dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z")})
    feature_id = model.insert_feature('audio', t, geojson.dumps(feature))




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
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = fname #str(uuid.uuid4()) + extn
        #body = self.request.data
        fh = open(__UPLOADS__ + cname, 'wb')
        fh.write(fileinfo['body'])
        self.finish(cname + " is uploaded!! Check %s folder" %__UPLOADS__)
        ingest_image_api(__UPLOADS__ + cname)

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
