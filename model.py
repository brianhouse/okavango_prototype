#!/usr/bin/env python3

import sqlite3, json, time, sys, os, geojson
from housepy import config, log

connection = sqlite3.connect("data.db")
connection.row_factory = sqlite3.Row
db = connection.cursor()

def init():
    try:
        db.execute("CREATE TABLE IF NOT EXISTS features (t INTEGER, kind TEXT, data TEXT)")
        db.execute("CREATE INDEX IF NOT EXISTS kind_t ON features(kind, t)")
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
init()

def insert_feature(kind, t, data):
    try:
        db.execute("INSERT INTO features (kind, t, data) VALUES (?, ?, ?)", (kind, t, data))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
    return entry_id

def fetch_features(kinds, start_t, stop_t):
    kindq = []
    for kind in kinds:
        kindq.append("OR kind='%s'" % kind)
    query = "SELECT rowid, data FROM features WHERE (1=0 %s) AND t>=? AND t<? ORDER BY t" % ''.join(kindq)
    db.execute(query, (start_t, stop_t))
    features = []
    for row in db.fetchall():
        feature = geojson.loads(row['data'])
        feature.id = row['rowid'] 
        features.append(feature)
    return features


