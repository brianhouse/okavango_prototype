#!/usr/bin/env python3

import geojson, csv, dateutil, datetime, model
from housepy import config, log, util, strings


sightings = []
headings = {}
with open("data/Sightings.csv") as f:
    rows = csv.reader(f)
    for r, row in enumerate(rows):
        if r == 0:
            for i, item in enumerate(row):
                headings[item.lower()] = i
            continue
        try:
            dt = util.parse_date("%s %s" % (row[headings['date']], row[headings['time']]), tz=config['local_tz'], dayfirst=True)
            t = util.timestamp(dt)
            coordinates = strings.as_numeric(row[headings['latitude']]), strings.as_numeric(row[headings['longitude']]), strings.as_numeric(row[headings['altitude']])
            properties = {'datetime': dt.strftime("%Y-%m-%dT%H:%M:%S%z"), 't_utc': t}
            for heading in headings:
                if heading not in ['date', 'time', 'latitude', 'longitude', 'altitude']:
                    try:
                        properties[heading] = strings.as_numeric(row[headings[heading]])
                    except IndexError:
                        pass
            feature = geojson.Feature(geometry={'type': "Point", 'coordinates': coordinates}, properties=properties)
            model.insert_feature("sighting", t, geojson.dumps(feature))
        except Exception as e:
            log.error("Row failed: " + log.exc(e))
            continue



"""

so namibia, botswana, and angola are all potentially different time zones


"""

