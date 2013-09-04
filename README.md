Okavango
========

Data streams from Dr. Steve Boyes trip down the delta

Issues
------
Image filenames -- microseconds?


Installation
------------

Python >=3.3

requires housepy

    sudo pip-3.3 install -r requirements.txt

install geojson from python 3 branch: https://github.com/brianhouse/geojson  
make sure your version of setuptools is upgraded


make sure the server is on top of the time:

    tzselect
    sudo ntpdate time.nist.gov  # in sudo crontab, daily


### Copyright/License

Copyright (c) 2013 Brian House and Jer Thorp

This code is released under the MIT License and is completely free to use for any purpose. See the LICENSE file for details.
