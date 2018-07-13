#!/usr/bin/env python

# Copyright (c) 2018, Stephen Goadhouse <sgoadhouse@virginia.edu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Neotion nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL NEOTION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#-------------------------------------------------------------------------------
#  Get a screen capture from Agilent/KeySight MSO3034A scope and save it to a file
#
# Using new MSOX3000 Class

# pyvisa 1.6 (or higher) (http://pyvisa.sourceforge.net/)
# pyvisa-py 0.2 (https://pyvisa-py.readthedocs.io/en/latest/)
#
# NOTE: pyvisa-py replaces the need to install NI VISA libraries
# (which are crappily written and buggy!) Wohoo!
#
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import random
import sys

# Set to the IP address of the oscilloscope
#@@@#agilent_msox_3034a = 'TCPIP0::172.28.36.206::INSTR'
agilent_msox_3034a = 'TCPIP0::mx3034a-sdg1.phys.virginia.edu::INSTR'

import argparse
parser = argparse.ArgumentParser(description='Get a screen capture from Agilent/KeySight MSO3034A scope and save it to a file')
parser.add_argument('ofile', nargs=1, help='Output file name')
args = parser.parse_args()

fn_ext = ".png"
pn = os.environ['HOME'] + "/Downloads"
fn = pn + "/" + args.ofile[0]

while os.path.isfile(fn + fn_ext):
     fn += "-" + random.choice("abcdefghjkmnpqrstuvwxyz")

fn += fn_ext

## IEEE Block handlers copied from python IVI: https://github.com/python-ivi/python-ivi/blob/master/ivi/ivi.py
##
## (NOTE: no longer needed since using similar functionality within PyVISA
#
def build_ieee_block(data):
    "Build IEEE block"
    # IEEE block binary data is prefixed with #lnnnnnnnn
    # where l is length of n and n is the
    # length of the data
    # ex: #800002000 prefixes 2000 data bytes
    return str('#8%08d' % len(data)).encode('utf-8') + data

    
def decode_ieee_block(data):
    "Decode IEEE block"
    # IEEE block binary data is prefixed with #lnnnnnnnn
    # where l is length of n and n is the
    # length of the data
    # ex: #800002000 prefixes 2000 data bytes
    if len(data) == 0:
        return b''
    
    ind = 0
    c = '#'.encode('utf-8')
    while data[ind:ind+1] != c:
        ind += 1
    
    ind += 1
    l = int(data[ind:ind+1])
    ind += 1
    
    if (l > 0):
        num = int(data[ind:ind+l].decode('utf-8'))
        ind += l
        
        return data[ind:ind+num]
    else:
        return data[ind:]

from msox3000 import MSOX3000

## Connect to the Power Supply with default wait time of 100ms
scope = MSOX3000(agilent_msox_3034a)
scope.open()

print(scope.idn())

print("Output file: %s" % fn )
scope.hardcopy(fn)
print('Done')

scope.close()
