#!/usr/bin/env python3

import sqlite3, json, time, sys, os
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
        kindq.append("OR kind = %s " % kind)
    db.execute("SELECT * FROM features WHERE (1=0 %s) AND t>=? AND t<? ORDER BY t" % kindq, (kind, start_t, stop_t))
    rows = [dict(feature) for feature in db.fetchall()]
    return rows 

