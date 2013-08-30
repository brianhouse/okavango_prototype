#!/usr/bin/env python3

import sqlite3, json, time, sys, os
from housepy import config, log

connection = sqlite3.connect("data.db")
connection.row_factory = sqlite3.Row
db = connection.cursor()

def init():
    try:
        db.execute("CREATE TABLE IF NOT EXISTS events (t INTEGER, kind TEXT, data TEXT)")
        db.execute("CREATE INDEX IF NOT EXISTS kind_t ON events(kind, t)")
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
init()

def insert_event(kind, t, data):
    try:
        db.execute("INSERT INTO events (kind, t, data) VALUES (?, ?, ?)", (device, kind, t, data))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
    return entry_id

def fetch_events(kind, start_t, stop_t):
    db.execute("SELECT * FROM events WHERE kind=? AND t>=? AND t<?", (kind, start_t, stop_t))
    rows = [dict(event) for event in db.fetchall()]
    return rows 

