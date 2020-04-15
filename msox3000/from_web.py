#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Copyright (c) 2020, Stephen Goadhouse <sgoadhouse@virginia.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
 
#-------------------------------------------------------------------------------
#  Since 2.50 firmware update of MSO-X 3000 Oscilloscope, started getting
#  Timeouts when accessing oscilloscope via SCPI. So this kludgy approach
#  uses the web interface of the oscilloscope to grab the screen image.
#
#  It is utilitarian for the moment but it is a working start.
#-------------------------------------------------------------------------------




import re
import pycurl
from os import environ
 
url = "http://192.168.153.80/"
path = "getImage.asp?inv=false" # can invert image with inv=true

#@@@#pattern = '<A HREF="/%s.*?">(.*?)</A>' % path
pattern = '<IMG .* SRC.*="(.*\.png)">'

outfilename = environ.get('HOME', '.')+"/Downloads/out.png"
print(outfilename)

from io import BytesIO

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, url+path)
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()

body = buffer.getvalue()
# Body is a byte string.
# We have to know the encoding in order to print it to a text file
# such as standard output.
print(body.decode('iso-8859-1'))

if (True):
    for filename in re.findall(pattern, body.decode('iso-8859-1')):
        print(filename)
        fp = open(outfilename, "wb")
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url+filename)
        curl.setopt(pycurl.WRITEDATA, fp)
        curl.perform()
        curl.close()
        fp.close()
