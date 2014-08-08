#!/usr/bin/env python3

import geojson, csv, dateutil, datetime, model, time, os, zipfile, pytz, xmltodict, json, shutil, urllib, math, subprocess
import xml.etree.ElementTree as ET        
from PIL import Image
from housepy import config, log, util, strings, emailer, net


def ingest_geo_feature(path, kind):
    log.info("ingest_geo_feature %s" % path)
    t_protect = model.get_protect(kind)
    sightings = []
    headings = {}
    with open(path) as f:
        rows = csv.reader(f)
        for r, row in enumerate(rows):
            if r == 0:
                for i, item in enumerate(row):
                    headings[item] = i
                continue
            try:
                dt = util.parse_date("%s %s" % (row[headings['Date']], row[headings['Time']]), tz=config['local_tz'], dayfirst=True)
                t = util.timestamp(dt)
                if t <= t_protect:
                    log.warning("Protected t, skipping...")
                    continue                
                try:
                    coordinates = strings.as_numeric(row[headings['Longitude']]), strings.as_numeric(row[headings['Latitude']]), strings.as_numeric(row[headings['Altitude']])
                except Exception as e:
                    log.error("Missing coordinates! Skipping...")
                    continue
                properties = {'DateTime': dt.strftime("%Y-%m-%dT%H:%M:%S%z"), 't_utc': t, 'ContentType': kind}
                for heading in headings:
                    if heading not in ['Date', 'Time', 'Latitude', 'Longitude', 'Altitude']:
                        try:
                            properties[heading] = strings.as_numeric(row[headings[heading]])
                        except IndexError:
                            pass
                feature = geojson.Feature(geometry={'type': "Point", 'coordinates': coordinates}, properties=properties)
                model.insert_feature(kind, t, geojson.dumps(feature))
            except Exception as e:
                log.error("Row failed: " + log.exc(e))
                continue


def ingest_ambit(path, t_protect):    
    log.info("ingest_ambit %s" % path)
    with open(path, 'r') as f:
        content = f.read()        
        content = content.split("<IBI>")[0]
        parts = content.split("</header>")
        header = parts[0] + "</header>"
        header = xmltodict.parse(header.encode('utf-8'))
        person = header['header']['Activity'].replace("OWBS ", "") 
        content = parts[-1].encode('utf-8')
        samples = xmltodict.parse(content)['Samples']['Sample']
        for s, sample in enumerate(samples):            
            try:
                if 'VerticalSpeed' not in sample:
                    # satellite data sample          
                    lon, lat, alt = None, None, None      
                    t, dt = None, None
                    for key, value in sample.items():
                        if key == "UTC":
                            dt = util.parse_date(sample['UTC']) # these are marked UTC in the data
                            t = util.timestamp(dt)
                            del sample[key]
                            continue
                        if key == "Longitude":
                            lon = math.degrees(float(sample['Longitude']))
                            del sample[key]                
                            continue                       
                        if key == "Latitude":
                            lat = math.degrees(float(sample['Latitude']))
                            del sample[key]               
                            continue
                        if key == "GPSAltitude":
                            alt = float(sample['Latitude'])
                            del sample[key]               
                            continue
                        if key[:3] == "Nav":
                            del sample[key]
                            continue
                        if type(value) != str:
                            del sample[key]
                            continue                            
                        sample[key] = strings.as_numeric(value) 
                    # if t <= t_protect:
                    #     log.warning("Protected t, skipping...")
                    #     continue
                    sample['DateTime'] = dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z")
                    sample['t_utc'] = t
                    sample['ContentType'] = 'ambit_geo'
                    sample['Person'] = person         
                    feature = geojson.Feature(geometry={'type': "Point", 'coordinates': [lon, lat, alt]}, properties=sample)            
                    model.insert_feature('ambit_geo', t, geojson.dumps(feature))

                else:
                    # energy data sample
                    for key, value in sample.items():
                        if key == "UTC":
                            dt = util.parse_date(value) # these are marked UTC in the data
                            t = util.timestamp(dt)
                            del sample[key]
                            continue
                        if type(value) != str:
                            del sample[key]
                            continue
                        sample[key] = strings.as_numeric(value)
                    # if t <= t_protect:
                    #     log.warning("Protected t, skipping...")
                    #     continue                        
                    sample['DateTime'] = dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z")
                    sample['t_utc'] = t
                    sample['ContentType'] = 'ambit'
                    sample['Person'] = person
                    feature = geojson.Feature(properties=sample)
                    model.insert_feature('ambit', t, geojson.dumps(feature))

            except Exception as e:
                log.error(log.exc(e))


def ingest_image(path, i, t_protect):
    log.info("ingest_image %s" % path)
    date_string = path.split('/')[-1] 
    dt = datetime.datetime.strptime(date_string.split('_')[0], "%d%m%Y%H%M")
    tz = pytz.timezone(config['local_tz'])
    dt = tz.localize(dt)
    t = util.timestamp(dt)
    # if t <= t_protect:
    #     log.warning("Protected t, skipping...")
    #     return                    
    try:
        image = Image.open(path)
        width, height = image.size    
    except Exception as e:
        log.error(log.exc(e))
        width, height = None, None        
    feature = geojson.Feature(properties={'utc_t': t, 'ContentType': "image", 'url': "/static/data/images/%s-%s.jpg" % (t, i), 'DateTime': dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z"), 'size': [width, height]})
    feature_id = model.insert_feature('image', t, geojson.dumps(feature))
    new_path = os.path.join(os.path.dirname(__file__), "static", "data", "images", "%s-%s.jpg" % (t, i))
    shutil.copy(path, new_path)

def ingest_audio(path, i, t_protect):
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

    log.debug("CONVERTING SOUND.")
    try:
        log.debug("--> converting [%s] to [%s]" % (fixed_path, new_path))
        log.debug("%s -y -i '%s' '%s'" % (config['ffmpeg'], os.path.abspath(fixed_path), os.path.abspath(new_path)))
        subprocess.check_call("%s -y -i '%s' '%s'" % (config['ffmpeg'], os.path.abspath(fixed_path), os.path.abspath(new_path)), shell=True)
    except Exception as e:
        log.error(log.exc(e))
        return

    log.debug("DONE CONVERTING SOUND.")
    feature = geojson.Feature(properties={'utc_t': t, 'ContentType': "audio", 'url': "/static/data/audio/%s-%s.wav" % (t, i), 'DateTime': dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z")})
    feature_id = model.insert_feature('audio', t, geojson.dumps(feature))


def ingest_beacon(content):
    log.info("ingest_beacon")
    t_protect = model.get_protect('beacon')    
    properties = {}
    coordinates = [None, None, None]
    t = None
    try:
        lines = content.split('\n')
        for line in lines:
            log.debug("%s" % line)
            try:
                if "Position Time:" in line:
                    line = line.replace("Position Time:", "").strip()
                    dt = util.parse_date(line)
                    t = util.timestamp(dt)
                    properties['DateTime'] = dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z")
                    properties['t_utc'] = t
                if "Map:" in line:
                    line = line.split('?')[1].strip()
                    result = net.urldecode(line)
                    lat, lon = result['q'].split(' ')[0].split(',')
                    coordinates[0], coordinates[1] = strings.as_numeric(lon), strings.as_numeric(lat)
                if "Altitude:" in line:
                    altitude = strings.as_numeric(line.replace("Altitude:", "").replace("meters", "").strip())
                    coordinates[2] = altitude
                if "Speed:" in line:
                    speed = strings.as_numeric(line.replace("Speed:", "").replace("Knots", "").strip())
                    properties['Speed'] = speed
                if "Heading:" in line:
                    heading = strings.as_numeric(line.replace("Heading:", "").replace("°", "").strip())
                    properties['Heading'] = heading
            except Exception as e:
                log.error(log.exc(e))
                continue
        # if t <= t_protect:
        #     log.warning("Protected t, skipping...")
        #     return                                
        feature = geojson.Feature(geometry={'type': "Point", 'coordinates': coordinates}, properties=properties)
        feature_id = model.insert_feature('beacon', t, geojson.dumps(feature))
    except Exception as e:
        log.error(log.exc(e))


def main():    
    messages = emailer.fetch()
    if len(messages) > 0:
        log.info("Fetched %s new messages..." % len(messages))
    for m, message in enumerate(messages):
        if message['from'] not in config['incoming']:
            log.warning("Received bunk email from %s" % message['from'])
            continue
        subject = message['subject'].lower().strip()
        log.info("Subject: %s" % subject)
        kind = None
        kinds = 'ambit', 'sighting', 'breadcrumb', 'image', 'audio'
        for k in kinds:        
            if util.lev_distance(k, subject) <= 2:
                kind = k
                break
        if kind is None and config['satellite'].lower() in subject:
            kind = 'beacon'
        if kind is None:
            log.error("subject not recognized")
        else:
            log.info("--> kind: %s" % kind)
        if kind == 'beacon':
            ingest_beacon(message['body'])
        else:
            log.info("--> %s attachments" % len(message['attachments']))
            for attachment in message['attachments']:

                try:
                    path = os.path.join(os.path.dirname(__file__), "data", "%s-%s_%s" % (util.timestamp(), m, attachment['filename'].lower()))
                    def write_file():
                        with open(path, 'wb') as f:
                            f.write(attachment['data'])

                    if kind in ('sighting', 'breadcrumb'):
                        if path[-3:] != "csv":
                            log.warning("--> expected csv file, got %s" % path)
                            continue
                        write_file()
                        ingest_geo_feature(path, kind)
                        break

                    elif kind in ('ambit', 'image', 'audio'): 
                        t_protect = model.get_protect(kind)
                        if path[-3:] != "zip":
                            log.warning("--> expected zip file, got %s" % path)
                            continue
                        write_file()            
                        if zipfile.is_zipfile(path) is False:
                            log.warning("--> zip file is corrupt %s" % path)
                            continue
                        p = path[:-4]
                        os.mkdir(p)
                        with zipfile.ZipFile(path, 'r') as archive:
                            archive.extractall(p)
                            def traverse(pd):
                                log.info("--> checking %s" % pd)
                                for i, filename in enumerate(os.listdir(pd)):
                                    if filename[0] == ".":
                                        continue
                                    elif os.path.isdir(os.path.join(pd, filename)):
                                        traverse(os.path.join(pd, filename))
                                    elif kind == 'ambit' and filename[-3:] == "xml":
                                        ingest_ambit(os.path.join(pd, filename), t_protect)
                                    elif kind == 'image' and filename[-3:] == "jpg":
                                        ingest_image(os.path.join(pd, filename), i, t_protect)
                                    elif kind == 'audio' and filename[-3:] == "mp3":
                                        ingest_audio(os.path.join(pd, filename), i, t_protect)
                                    else:
                                        log.warning("--> unknown file type %s, skipping..." % filename)
                            traverse(p)
                        break

                except Exception as e:
                    log.error(log.exc(e))

main()
