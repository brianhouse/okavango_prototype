#!/usr/bin/env python3

import geojson, csv, dateutil, datetime
from housepy import config, log, util, strings

LOCALTZ = config['local_tz']

# p = geojson.Feature(id=4, coordinates=[39.7392, 104.9847], properties={'big': True})
# c = geojson.FeatureCollection([p])

# print(c)
# print(geojson.dumps(c, indent=4))


sightings = []
headings = {}
with open("Sightings.csv") as f:
    rows = csv.reader(f)
    for r, row in enumerate(rows):
        if r == 0:
            for i, item in enumerate(row):
                headings[item.lower()] = i
            continue
        try:
            dt = util.parse_date("%s %s" % (row[headings['date']], row[headings['time']]), tz=LOCALTZ, dayfirst=True)
            t = util.timestamp(dt)
            coordinates = strings.as_numeric(row[headings['latitude']]), strings.as_numeric(row[headings['longitude']]), strings.as_numeric(row[headings['altitude']])
            print(dt)
            print(datetime.datetime.fromtimestamp(t))
            exit()
            properties = {'datetime': dt.strftime("%Y-%m-%dT%H:%M:%S%z"), 't': t}
            for heading in headings:
                if heading not in ['date', 'time', 'latitude', 'longitude', 'altitude']:
                    try:
                        properties[heading] = strings.as_numeric(row[headings[heading]])
                    except IndexError:
                        pass
            feature = geojson.Feature(geometry={'type': "Point", 'coordinates': coordinates}, properties=properties)
            print(geojson.dumps(feature, indent=4))
            print(dt)
        except Exception as e:
            log.error("Row failed: " + log.exc(e))
            continue



"""

so namibia, botswana, and angola are all potentially different time zones


"""

