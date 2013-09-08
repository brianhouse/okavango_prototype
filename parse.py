#!/usr/bin/env python3

import geojson, csv, dateutil, datetime, model, time, os, zipfile, pytz, xmltodict, json, shutil, urllib
import xml.etree.ElementTree as ET        
from housepy import config, log, util, strings, emailer, net


def injest_geo_feature(path, kind):
    log.info("injest_geo_feature %s" % path)
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


def injest_ambit(path):    
    log.info("injest_ambit %s" % path)
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
            if 'VerticalSpeed' not in sample:
                continue
            for key, value in sample.items():
                if key == "UTC":
                    dt = util.parse_date(value) # these are UTC in the data
                    t = util.timestamp(dt)
                    del sample[key]
                    continue
                if type(value) != str:
                    del sample[key]
                    continue
                sample[key] = strings.as_numeric(value)
            sample['DateTime'] = dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z")
            sample['t_utc'] = t
            sample['ContentType'] = 'ambit'
            sample['Person'] = person
            feature = geojson.Feature(properties=sample)
            model.insert_feature('ambit', t, geojson.dumps(feature))


def injest_image(path):
    log.info("injest_image %s" % path)
    dt = datetime.datetime.strptime(path.split('/')[-1].split('_')[0], "%d%m%Y%H%M")
    dt.replace(microsecond=int(path[-7:-4]))
    tz = pytz.timezone(config['local_tz'])
    dt = tz.localize(dt)
    t = util.timestamp(dt)
    feature = geojson.Feature(properties={'utc_t': t, 'ContentType': "image", 'url': "/static/data/images/%s.jpg" % t})
    feature_id = model.insert_feature('image', t, geojson.dumps(feature))
    new_path = os.path.join(os.path.dirname(__file__), "static", "data", "images", "%s.jpg" % t)
    shutil.copy(path, new_path)


def injest_audio(path):
    log.info("injest_audio %s" % path)
    dt = datetime.datetime.strptime(path.split('/')[-1], "audio %d%m%Y_%H%M.mp3")
    tz = pytz.timezone(config['local_tz'])
    dt = tz.localize(dt)
    t = util.timestamp(dt)
    feature = geojson.Feature(properties={'utc_t': t, 'ContentType': "audio", 'url': "/static/data/audio/%s.mp3" % t, 'DateTime': dt.astimezone(pytz.timezone(config['local_tz'])).strftime("%Y-%m-%dT%H:%M:%S%z")})
    feature_id = model.insert_feature('audio', t, geojson.dumps(feature))
    new_path = os.path.join(os.path.dirname(__file__), "static", "data", "audio", "%s.mp3" % t)
    shutil.copy(path, new_path)


def injest_beacon(content):
    log.info("injest_beacon")
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
        feature = geojson.Feature(geometry={'type': "Point", 'coordinates': coordinates}, properties=properties)
        feature_id = model.insert_feature('beacon', t, geojson.dumps(feature))
    except Exception as e:
        log.error(log.exc(e))


messages = emailer.fetch()
for message in messages:
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
        injest_beacon(message['body'])
    else:
        log.info("--> %s attachments" % len(message['attachments']))
        for attachment in message['attachments']:

            try:
                path = os.path.join(os.path.dirname(__file__), "data", "%s_%s" % (util.timestamp(), attachment['filename'].lower()))
                def write_file():
                    with open(path, 'wb') as f:
                        f.write(attachment['data'])

                if kind in ('sighting', 'breadcrumb'):
                    if path[-3:] != "csv":
                        log.warning("--> expected csv file, got %s" % path)
                        continue
                    write_file()
                    injest_geo_feature(path, kind)
                    break

                elif kind in ('ambit', 'image', 'audio'): 
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
                        for filename in os.listdir(p):
                            if kind == 'ambit' and filename[-3:] == "xml":
                                injest_ambit(os.path.join(p, filename))
                            elif kind == 'image' and filename[-3:] == "jpg":
                                injest_image(os.path.join(p, filename))
                            elif kind == 'audio' and filename[-3:] == "mp3":
                                injest_audio(os.path.join(p, filename))
                            else:
                                log.warning("--> unknown file type %s, skipping..." % filename)
                    break

            except Exception as e:
                log.error(log.exc(e))

