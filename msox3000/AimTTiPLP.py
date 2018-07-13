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
#  Control a Aim TTi PL-P Series DC Power Supplies with PyVISA
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
import re

class AimTTiPLP(SCPI):
    """Basic class for controlling and accessing an Aim TTi PL-P Series
    Power Supply. This series of power supplies only minimally adheres
    to any LXI specifications and so it uses its own commands although
    it adheres to the basic syntax of SCPI. The underlying accessor
    functions of SCPI.py are used but the top level are all re-written
    below to handle the very different command syntax. This shows how
    one might add packages to support other such power supplies that
    only minimally adhere to the command standards.
    """

    def __init__(self, resource, wait=1.0):
        """Init the class with the instruments resource string

        resource - resource string or VISA descriptor, like TCPIP0::192.168.1.100::9221::SOCKET 
        wait     - float that gives the default number of seconds to wait after sending each command

        NOTE: According to the documentation for this power supply, the
        resource string when using the Ethernet access method must look
        like TCPIP0::192.168.1.100::9221::SOCKET where 192.168.1.100 is
        replaced with the specific IP address of the power supply. The
        inclusion of the 9221 port number and SOCKET keyword are
        apparently mandatory for these power supplies.
        """
        super(AimTTiPLP, self).__init__(resource, max_chan=3, wait=wait,
                                        cmd_prefix='',
                                        read_termination='\n',
                                        write_termination='\r\n')

    def setLocal(self):
        """Set the power supply to LOCAL mode where front panel keys work again
        """
        self._instWrite('LOCAL')
    
    def setRemote(self):
        """Set the power supply to REMOTE mode where it is controlled via VISA
        """
        # Not supported explicitly by this power supply but the power
        # supply does switch to REMOTE automatically. So send any
        # command to do it.
        self._instWrite('*WAI')
    
    def setRemoteLock(self):
        """Set the power supply to REMOTE Lock mode where it is
           controlled via VISA & front panel is locked out
        """
        self._instWrite('IFLOCK')

    def beeperOn(self):
        """Enable the system beeper for the instrument"""
        # NOTE: Unsupported command by this power supply. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass
        
    def beeperOff(self):
        """Disable the system beeper for the instrument"""
        # NOTE: Unsupported command by this power supply. However,
        # instead of raising an exception and breaking any scripts,
        # simply return quietly.
        pass
        
    def isOutputOn(self, channel=None):
        """Return true if the output of channel is ON, else false
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        str = 'OP{}?'.format(self.channel)
        ret = self._instQuery(str)

        # Only check first character so that there can be training whitespace that gets ignored
        if (ret[0] == '1'):
            return True
        else:
            return False
    
    def outputOn(self, channel=None, wait=None):
        """Turn on the output for channel
        
           wait    - number of seconds to wait after sending command
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait
            
        str = 'OP{} 1'.format(self.channel)
        self._instWrite(str)
        sleep(wait)             # give some time for PS to respond
    
    def outputOff(self, channel=None, wait=None):
        """Turn off the output for channel
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
                    
        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait
            
        str = 'OP{} 0'.format(self.channel)
        self._instWrite(str)
        sleep(wait)             # give some time for PS to respond
    
    def outputOnAll(self, wait=None):
        """Turn on the output for ALL channels
        
        """

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        str = 'OPALL 1'.format(self.channel)
        self._instWrite(str)
        sleep(wait)             # give some time for PS to respond
    
    def outputOffAll(self, wait=None):
        """Turn off the output for ALL channels
        
        """

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        str = 'OPALL 0'.format(self.channel)
        self._instWrite(str)
        sleep(wait)             # give some time for PS to respond
    
    def setVoltage(self, voltage, channel=None, wait=None):
        """Set the voltage value for the channel
        
           voltage - desired voltage value as a floating point number
           wait    - number of seconds to wait after sending command
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait
            
        str = 'V{} {}'.format(self.channel, voltage)
        self._instWrite(str)
        sleep(wait)             # give some time for PS to respond
        
    def setCurrent(self, current, channel=None, wait=None):
        """Set the current value for the channel
        
           current - desired current value as a floating point number
           channel - number of the channel starting at 1
           wait    - number of seconds to wait after sending command
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait
            
        str = 'I{} {}'.format(self.channel, current)
        self._instWrite(str)
        sleep(wait)             # give some time for PS to respond

        
    def queryVoltage(self, channel=None):
        """Return what voltage set value is (not the measured voltage,
        but the set voltage)
        
        channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        str = 'V{}?'.format(self.channel)
        ret = self._instQuery(str)

        # Pull out words from response
        match = re.match('^([^\s0-9]+)([0-9]+)\s+([0-9.+-]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 3):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[0] != 'V' or int(words[1]) != self.channel):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[2])
    
    def queryCurrent(self, channel=None):
        """Return what current set value is (not the measured current,
        but the set current)
        
        channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
                    
        str = 'I{}?'.format(self.channel)
        ret = self._instQuery(str)

        # Pull out words from response
        match = re.match('^([^\s0-9]+)([0-9]+)\s+([0-9.+-]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 3):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[0] != 'I' or int(words[1]) != self.channel):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[2])
    
    def measureVoltage(self, channel=None):
        """Read and return a voltage measurement from channel
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
                    
        str = 'V{}O?'.format(self.channel)
        ret = self._instQuery(str)

        # Pull out words from response
        match = re.match('^([0-9.+-]+)([^\s]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 2):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[1] != 'V'):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[0])
    
    def measureCurrent(self, channel=None):
        """Read and return a current measurement from channel
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        str = 'I{}O?'.format(self.channel)
        ret = self._instQuery(str)

        # Pull out words from response
        match = re.match('^([0-9.+-]+)([^\s]+)',ret)
        if (match == None):
            raise RuntimeError('Unexpected response: "{}"'.format(ret))
        else:
            # break out the words from the response
            words = match.groups()
            if (len(words) != 2):
                raise RuntimeError('Unexpected number of words in response: "{}"'.format(ret))
            elif(words[1] != 'A'):
                raise ValueError('Unexpected response format: "{}"'.format(ret))
            else:
                # response checks out so return the fixed point response as a float()
                return float(words[0])
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Access and control a Aim TTi PL-P Series power supply')
    parser.add_argument('chan', nargs='?', type=int, help='Channel to access/control (starts at 1)', default=1)
    args = parser.parse_args()

    from time import sleep
    from os import environ
    resource = environ.get('TTIPLP_IP', 'TCPIP0::192.168.1.100::9221::SOCKET')
    ttiplp = AimTTiPLP(resource)
    ttiplp.open()

    ## set Remote Lock On
    #ttiplp.setRemoteLock()
    
    ttiplp.beeperOff()
    
    if not ttiplp.isOutputOn(args.chan):
        ttiplp.outputOn()
        
    print('Ch. {} Settings: {:6.4f} V  {:6.4f} A'.
              format(args.chan, ttiplp.queryVoltage(),
                         ttiplp.queryCurrent()))

    voltageSave = ttiplp.queryVoltage()
    
    #print(ttiplp.idn())
    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ttiplp.setVoltage(2.7)

    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ttiplp.setVoltage(2.3)

    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ttiplp.setVoltage(voltageSave)

    print('{:6.4f} V'.format(ttiplp.measureVoltage()))
    print('{:6.4f} A'.format(ttiplp.measureCurrent()))

    ## turn off the channel
    ttiplp.outputOff()

    ttiplp.beeperOn()

    ## return to LOCAL mode
    ttiplp.setLocal()
    
    ttiplp.close()
