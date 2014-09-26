#!/usr/bin/env python3

# The purpose of this script is to bind latlon of photos, tweets to more accurate points
# ie - from beacons to ambit paths

c = 0;

import geojson, model

query = "SELECT * FROM features WHERE kind = 'tweet' OR kind = 'image'"
model.db.execute(query)

for row in db.fetchall():

	t = row['t']
	k = row['kind']
	d = row['data']

	#get new coords
	coords = model.get_coords_by_time(t);

	#load json from data column
	feature = geojson.loads(d)

	#frankenfeature
	newFeature = geojson.Feature(geometry=coords,properties=feature.properties)

	newData = json.dumps(newFeature)
	print("OLD" + d)
	print("NEW" + newData)

	#insert
	#db.execute("UPDATE features SET data=" + newData + " WHERE t=" + t " AND kind=" + k)

	c = c + 1;

	print(c);
	

