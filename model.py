#!/usr/bin/env python3

import sqlite3, json, time, sys, os, geojson
from housepy import config, log, util

def db_call(f):
    def wrapper(*args):
        connection = sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), "data.db")))
        connection.row_factory = sqlite3.Row
        db = connection.cursor()
        results = f(db, *args)
        connection.commit()
        connection.close()
        return results
    return wrapper

@db_call
def init(db):
    try:
        db.execute("CREATE TABLE IF NOT EXISTS features (t INTEGER, kind TEXT, data TEXT, t_created INTEGER)")
        db.execute("CREATE INDEX IF NOT EXISTS kind_t ON features(kind, t)")
        db.execute("CREATE TABLE IF NOT EXISTS hydrodrops (t INTEGER, id TEXT, lat REAL, lon REAL, t_created INTEGER)")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS id_lat_lon ON hydrodrops(id, lat, lon)")
    except Exception as e:
        log.error(log.exc(e))
        return
init()

@db_call
def insert_feature(db, kind, t, data):
    try:
        db.execute("INSERT INTO features (kind, t, data, t_created) VALUES (?, ?, ?, ?)", (kind, t, data, util.timestamp()))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    log.info("Inserted feature (%s) %s" % (entry_id, t))    
    return entry_id

@db_call
def insert_hydrodrop(db, t, hydrosensor_id, lat, lon):
    try:
        db.execute("INSERT INTO hydrodrops (t, id, lat, lon, t_created) VALUES (?, ?, ?, ?, ?)", (t, hydrosensor_id, float(lat), float(lon), util.timestamp()))
        hydrodrop_id = db.lastrowid        
    except Exception as e:
        log.error(log.exc(e))
        return
    log.info("Inserted hydrodrop (%s) %s %s" % (hydrodrop_id, hydrosensor_id, t))  
    return hydrodrop_id  

@db_call
def fetch_features(db, kinds, start_t, stop_t, skip=1):
    kindq = []
    for kind in kinds:
        kindq.append(" OR kind='%s'" % kind)
    query = "SELECT rowid, data FROM features WHERE rowid %% ? = 0 AND (1=0%s) AND t>=? AND t<? ORDER BY t" % ''.join(kindq)
    log.debug(query)
    db.execute(query, (skip, start_t, stop_t))
    features = []
    # this is slow
    for row in db.fetchall():
        feature = geojson.loads(row['data'])
        feature.id = row['rowid'] 
        features.append(feature)
    return features

@db_call
def get_protect(db, kind):
    db.execute("SELECT t FROM features WHERE kind=? ORDER BY t DESC LIMIT 1", (kind,))
    result = db.fetchone()
    if result is None:
        return 0
    return result['t']

@db_call
def get_coords_by_time(db, time):
    db.execute("SELECT t,data FROM features WHERE kind='ambit_geo' AND t < ? ORDER BY t DESC LIMIT 1", (time,))
    result = db.fetchone()
    print(result)
    closeFeature = result['data'];
    j = json.loads(closeFeature);
    geom = j['geometry'];

    print("CLOSEST FEATURE TO ? IS ?", (time,geom))
    return geom;

@db_call
def update_latlon(db):
    query = "SELECT * FROM features WHERE kind = 'tweet' OR kind = 'image' AND t > 1408171925"
    db.execute(query)

    c = 0;

    for row in db.fetchall():

        t = row['t']
        k = row['kind']
        d = row['data']

        print(t)

        #get new coords
        coords = get_coords_by_time(t);

        #load json from data column
        feature = geojson.loads(d)

        #frankenfeature
        newFeature = geojson.Feature(geometry=coords,properties=feature.properties)

        newData = json.dumps(newFeature)
        print("OLD" + d)
        print("NEW" + newData)

        #insert
        db.execute("UPDATE features SET data=" + newData + " WHERE t=" + t " AND kind=" + k)

        c = c + 1;

        print(c);

@db_call
def get_drop_by_id(db, hydrosensor_id):
    db.execute("SELECT lat, lon FROM hydrodrops WHERE id=? ORDER BY t DESC LIMIT 1", (hydrosensor_id,))
    result = db.fetchone()
    if result is not None:
        return result['lat'], result['lon']
    return None, None

@db_call
def db_query(db, query):
    db.execute(query)
    return db.fetchall()

# http://stackoverflow.com/questions/14511337/efficiency-of-reopening-sqlite-database-after-each-query
# unless youre doing a ton of statements each time, opening it each time isnt going to be much of a problem