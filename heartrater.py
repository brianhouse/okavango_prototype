#!/usr/bin/env python3

import geojson
from housepy import config, log, drawing
from model import db
import signal_processing as sp
import numpy as np

log.info("Loading data...")

t = 1379224903

query = "SELECT rowid, data FROM features WHERE kind='ambit' AND t>=%s AND t<(%s+(4*24*60*60)) ORDER BY t" % (t, t)
db.execute(query)
hrs = []
ts = []
rows = db.fetchall()
log.info("%s results" % len(rows))
for row in rows:
    feature = geojson.loads(row['data'])
    try:
        if feature['properties']['Person'] != "GB":
            continue
        hr = feature['properties']['HR']
        t = feature['properties']['t_utc']
    except Exception as e:
        # log.warning(e)
        continue
    hrs.append(hr)
    ts.append(t)

log.info("--> done")

log.info("Processing...")
total_time = ts[-1] - ts[0]
total_samples = int(total_time / 60)     # once per minute

print(total_time)
print(total_samples)

signal = sp.resample(ts, hrs, total_samples)
signal = sp.normalize(signal)
signal = signal - sp.smooth(signal, size=100)   # flatten it out a bit
threshold = np.average(signal) + (2 * np.std(signal))   # threshold is average plus 2 std deviation
smoothed_signal = sp.smooth(signal, size=10)
peaks, valleys = sp.detect_peaks(smoothed_signal, lookahead=10, delta=.001)
max_peak = max(peaks, key=lambda p: p[1])
log.info("max_peak %s" % max_peak)
peaks = [peak for peak in peaks if peak[1] > threshold]

def draw():
    log.info("--> done")
    log.info("Plotting...")
    ctx = drawing.Context()
    ctx.plot(signal)
    ctx.plot(smoothed_signal, stroke=(100, 0, 0))
    for peak in peaks:
        ctx.arc(peak[0] / total_samples, peak[1], 10.0 / ctx.width, stroke=(0, 255, 0), thickness=5)
    ctx.line(0, threshold, 1.0, threshold, stroke=(0, 0, 255))
    ctx.output("screenshots")
draw()

peaks = [[t + (peak[0] * 60), (peak[1] - threshold) / max_peak[1]] for peak in peaks if peak[1] > threshold]
print(peaks)

