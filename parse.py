#!/usr/bin/env python3

import geojson, csv, dateutil, datetime, model, time, os, zipfile, pytz
from housepy import config, log, util, strings, emailer


def injest_geo_feature(filename, kind):
    sightings = []
    headings = {}
    with open(filename) as f:
        rows = csv.reader(f)
        for r, row in enumerate(rows):
            if r == 0:
                for i, item in enumerate(row):
                    headings[item.lower()] = i
                continue
            try:
                dt = util.parse_date("%s %s" % (row[headings['date']], row[headings['time']]), tz=config['local_tz'], dayfirst=True)
                t = util.timestamp(dt)
                try:
                    coordinates = strings.as_numeric(row[headings['latitude']]), strings.as_numeric(row[headings['longitude']]), strings.as_numeric(row[headings['altitude']])
                except Exception as e:
                    log.error("Missing coordinates! Skipping...")
                    continue
                properties = {'datetime': dt.strftime("%Y-%m-%dT%H:%M:%S%z"), 't_utc': t, 'contenttype': kind}
                for heading in headings:
                    if heading not in ['date', 'time', 'latitude', 'longitude', 'altitude']:
                        try:
                            properties[heading] = strings.as_numeric(row[headings[heading]])
                        except IndexError:
                            pass
                feature = geojson.Feature(geometry={'type': "Point", 'coordinates': coordinates}, properties=properties)
                model.insert_feature(kind, t, geojson.dumps(feature))
                log.info("Inserted feature")
            except Exception as e:
                log.error("Row failed: " + log.exc(e))
                continue


def injest_ambit():    
    pass
    

def injest_media(filename, kind):
    dt = datetime.datetime.strptime(filename.split('_')[0], "%d%m%Y%H%M")
    dt.replace(microsecond=int(filename[-7:3]))
    log.debug(dt)
    tz = pytz.timezone(config['local_tz'])
    dt = tz.localize(dt)
    t = util.timestamp(dt)



messages = emailer.fetch()
for message in messages:
    if message['from'] not in config['incoming']:
        log.warning("Received bunk email from %s" % message['from'])
        continue
    # notes = None
    # if 'body' in message:
    #     notes = message['body']
    # elif 'html' in message:
    #     notes = strings.strip_html(message['html'])
    # if notes is not None:
    #     injest_note(note)
    subject = message['subject'].lower().strip()
    kind = None
    kinds = 'ambit', 'sighting', 'breadcrumb', 'image', 'audio'
    for k in kinds:        
        if util.lev_distance(k, subject) <= 2:
            kind = k
            break
    if kind is None and 'TS270140' in subject:
        kind = 'position'
    if kind is None:
        log.error("subject not recognized")
        break
    for attachment in message['attachments']:

        try:
            path = os.path.join(os.path.dirname(__file__), "data", "%s_%a" % (util.timestamp(), attachment['filename'].lower()))
            def write_file():
                with open(path, 'wb') as f:
                    f.write(attachment['data'])

            if kind in ('sighting', 'breadcrumb'):
                if path[-3:] != "csv":
                    continue
                write_file()
                injest_geo_feature(path, kind)
                break

            elif kind in ('ambit', 'image', 'audio'): 
                if zipfile.is_zipfile(path) is False:
                    continue
                write_file()            
                p = path.split('.')[0]
                os.mkdir(p)
                with ZipFile(path, 'r') as archive:
                archive.extractall(p)
                for filename in os.listdir(p):
                    if kind == 'ambit':
                        injest_ambit(os.path.join(p, filename))
                    elif kind == 'image' or kind == 'audio':
                        injest_media(os.path.join(p, filename), kind)

            elif kind == 'position':
                pass

        except Exception as e:
            log.error(log.exc(e))


