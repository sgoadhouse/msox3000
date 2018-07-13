#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Copyright (c) 2018, Stephen Goadhouse <sgoadhouse@virginia.edu>
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
#  Control of HP/Agilent/Keysight MSO-X/DSO-X 3000A Oscilloscope with PyVISA
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    from . import SCPI
except ValueError:
    from SCPI import SCPI
    
from time import sleep
import visa

class MSOX3000(SCPI):
    """Basic class for controlling and accessing a HP/Agilent/Keysight MSO-X/DSO-X 3000A Oscilloscope"""

    def __init__(self, resource, wait=0):
        """Init the class with the instruments resource string

        resource - resource string or VISA descriptor, like TCPIP0::172.16.2.13::INSTR
        wait     - float that gives the default number of seconds to wait after sending each command
        """
        super(MSOX3000, self).__init__(resource, max_chan=4, wait=wait, cmd_prefix=':')


    # =========================================================
    # Based on the screen image download example the MSO-X 3000 Programming
    # Guide and modified to work within this class ...
    # =========================================================
    def hardcopy(self, filename):
        """ Download the screen image to the given filename. """

        self._instWrite(":HARDcopy:INKSaver OFF")
        scrImage = self._instWriteIEEEBlock(":DISPlay:DATA? PNG, COLor")

        # Save display data values to file.
        f = open(filename, "wb")
        f.write(scrImage)
        f.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Access and control a MSO-X/DSO-X 3000 Oscilloscope')
    parser.add_argument('chan', nargs='?', type=int, help='Channel to access/control (starts at 1)', default=1)
    args = parser.parse_args()

    from time import sleep
    from os import environ
    resource = environ.get('MSOX3000_IP', 'TCPIP0::172.16.2.13::INSTR')
    instr = MSOX3000(resource)
    instr.open()

    ## set Remote Lock On
    #instr.setRemoteLock()
    
    instr.beeperOff()
    
    if not instr.isOutputOn(args.chan):
        instr.outputOn()
        
    print('Ch. {} Settings: {:6.4f} V  {:6.4f} A'.
              format(args.chan, instr.queryVoltage(),
                         instr.queryCurrent()))

    voltageSave = instr.queryVoltage()
    
    #print(instr.idn())
    print('{:6.4f} V'.format(instr.measureVoltage()))
    print('{:6.4f} A'.format(instr.measureCurrent()))

    instr.setVoltage(2.7)

    print('{:6.4f} V'.format(instr.measureVoltage()))
    print('{:6.4f} A'.format(instr.measureCurrent()))

    instr.setVoltage(2.3)

    print('{:6.4f} V'.format(instr.measureVoltage()))
    print('{:6.4f} A'.format(instr.measureCurrent()))

    instr.setVoltage(voltageSave)

    print('{:6.4f} V'.format(instr.measureVoltage()))
    print('{:6.4f} A'.format(instr.measureCurrent()))

    ## turn off the channel
    instr.outputOff()

    instr.beeperOn()

    ## return to LOCAL mode
    instr.setLocal()
    
    instr.close()
