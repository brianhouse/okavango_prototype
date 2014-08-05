#!/usr/bin/env python3

import sqlite3, json, time, sys, os, geojson
from housepy import config, log, util

connection = sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), "data.db")))
connection.row_factory = sqlite3.Row
db = connection.cursor()

def init():
    try:
        db.execute("CREATE TABLE IF NOT EXISTS features (t INTEGER, kind TEXT, data TEXT, t_created INTEGER)")
        db.execute("CREATE INDEX IF NOT EXISTS kind_t ON features(kind, t)")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS t_kind ON features(t, kind)")
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
init()

def insert_feature(kind, t, data):
    try:
        db.execute("INSERT INTO features (kind, t, data, t_created) VALUES (?, ?, ?, ?)", (kind, t, data, util.timestamp()))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
    log.info("Inserted feature (%s) %s" % (entry_id, t))    
    return entry_id

def fetch_features(kinds, start_t, stop_t, skip=1):
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

def get_protect(kind):
    db.execute("SELECT t FROM features WHERE kind=? ORDER BY t DESC LIMIT 1", (kind,))
    result = db.fetchone()
    if result is None:
        return 0
    return result['t']

