#!/usr/bin/env python3

"""
To be run once after data is collected. Future versions to be run on the fly.

could use more safety checks and outlier elimination.

"""

import geojson, model
from housepy import config, log, strings
from model import db
import signal_processing as sp
import numpy as np

log.info("Loading data...")

start_t = 1377993600#1379224903
stop_t = start_t + (30*24*60*60)

geo = model.fetch_features(['ambit_geo'], start_t, stop_t)
log.info("--> got geo: %s" % len(geo))

query = "SELECT rowid, data FROM features WHERE kind='ambit' AND t>=%s AND t<%s ORDER BY t" % (start_t, stop_t)
db.execute(query)
hrs = []
ts = []
rows = db.fetchall()
log.info("%s results" % len(rows))


for person in ('John', 'Steve', 'GB'):

    log.info("Scanning for %s" % person)

    for row in rows:
        feature = geojson.loads(row['data'])
        try:
            if feature['properties']['Person'] != person:
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

    log.debug("last_t %s" % ts[-1])
    log.debug("total_time %s" % total_time)
    log.debug("total_time_f %s" % strings.format_time(total_time))
    log.debug("total_samples %s" % total_samples)
    sample_length = total_time / total_samples
    log.debug("sample_length %s" % sample_length)

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
        from housepy import drawing
        log.info("--> done")
        log.info("Plotting...")
        ctx = drawing.Context()
        ctx.plot(signal)
        ctx.plot(smoothed_signal, stroke=(100, 0, 0))
        for peak in peaks:
            ctx.arc(peak[0] / total_samples, peak[1], 10.0 / ctx.width, stroke=(0, 255, 0), thickness=5)
        ctx.line(0, threshold, 1.0, threshold, stroke=(0, 0, 255))
        ctx.output("screenshots")
    # draw()

    peaks = [[start_t + (peak[0] * 60), (peak[1] - threshold) / max_peak[1]] for peak in peaks]

    i = 0
    for peak in peaks:
        while i<len(geo) and geo[i]['properties']['t_utc'] < peak[0]:
            i += 1
        if i == 0 or i == len(geo):
            log.debug("skipped %s" % peak)
            continue
        i -= 1
        feature = geojson.Feature(geometry=geo[i]['geometry'], properties={'Intensity': peak[1], 't_utc': peak[0], 'Person': person})
        model.insert_feature('heart_spike', peak[0], geojson.dumps(feature))

        # print(geojson.dumps(feature, indent=4))

        # we're still skipping some, dont know what that's about



