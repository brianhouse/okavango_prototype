#!/usr/bin/env python3

import geojson, csv, dateutil, datetime, model, time, os
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


def injest_note(note):
    """These wouldnt be geocoded, right? so what format do they live in?"""

# def injest_image():

# def injest_audio():    

# etc


messages = emailer.fetch()
for message in messages:
    if message['from'] != config['incoming']:
        log.warning("Received bunk email from %s" % message['from'])
        continue
    notes = None
    if 'body' in message:
        notes = message['body']
    elif 'html' in message:
        notes = strings.strip_html(message['html'])
    if notes is not None:
        injest_note(note)
    for attachment in message['attachments']:
        filename = os.path.join(os.path.dirname(__file__), "data", "%s_%a" % (int(time.time()), attachment['filename'].lower()))
        with open(filename, 'wb') as f:
            f.write(attachment['data'])
        if "sighting" in filename:
            injest_geo_feature(filename, "sighting")
        elif "breadcrumbs" in filename:
            injest_geo_feature(filename, "position")



"""

so namibia, botswana, and angola are all potentially different time zones


"""

