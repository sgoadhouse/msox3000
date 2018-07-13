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
#  Control DC Power Supplies using standard SCPI commands with PyVISA
#
# For more information on SCPI, see:
# https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments
# http://www.ivifoundation.org/docs/scpi-99.pdf
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from time import sleep
import visa

class SCPI(object):
    """Basic class for controlling and accessing a Power Supply with Standard SCPI Commands"""

    def __init__(self, resource, max_chan=1, wait=1.0,
                     cmd_prefix = '',
                     read_termination = '',
                     write_termination = ''):
        """Init the class with the instruments resource string

        resource   - resource string or VISA descriptor, like TCPIP0::172.16.2.13::INSTR
        max_chan   - number of channels in power supply
        wait       - float that gives the default number of seconds to wait after sending each command
        cmd_prefix - optional command prefix (ie. some instruments require a ':' prefix)
        read_termination - optional read_termination parameter to pass to open_resource()
        write_termination - optional write_termination parameter to pass to open_resource()
        """
        self._resource = resource
        self._max_chan = max_chan                # number of channels
        self._wait = wait
        self._prefix = cmd_prefix
        self._curr_chan = 1                      # set the current channel to the first one
        self._read_termination = read_termination
        self._write_termination = write_termination
        self._inst = None        

    def open(self):
        """Open a connection to the VISA device with PYVISA-py python library"""
        self._rm = visa.ResourceManager('@py')
        self._inst = self._rm.open_resource(self._resource,
                                            read_termination=self._read_termination,
                                            write_termination=self._write_termination)

    def close(self):
        """Close the VISA connection"""
        self._inst.close()

    @property
    def channel(self):
        return self._curr_chan
    
    @channel.setter
    def channel(self, value):
        if (value < 1) or (value > self._max_chan):
            raise ValueError('Invalid channel number: {}. Must be between {} and {}, inclusive.'.
                                 format(channel, 1, self._max_chan))
        self._curr_chan = value

    def _instQuery(self, queryStr):
        if (queryStr[0] != '*'):
            queryStr = self._prefix + queryStr
        #print("QUERY:",queryStr)
        return self._inst.query(queryStr)
        
    def _instWrite(self, writeStr):
        if (writeStr[0] != '*'):
            writeStr = self._prefix + writeStr
        #print("WRITE:",writeStr)
        return self._inst.write(writeStr)
        
    def _chStr(self, channel):
        """return the channel string given the channel number and using the format CHx"""

        return 'CH{}'.format(channel)
    
    def _chanStr(self, channel):
        """return the channel string given the channel number and using the format x"""

        return '{}'.format(channel)
    
    def _onORoff(self, str):
        """Check if string says it is ON or OFF and return True if ON
        and False if OFF
        """

        # Only check first two characters so do not need to deal with
        # trailing whitespace and such
        if str[:2] == 'ON':
            return True
        else:
            return False
        
    def _wait(self):
        """Wait until all preceeding commands complete"""
        #self._instWrite('*WAI')
        self._instWrite('*OPC')
        wait = True
        while(wait):
            ret = self._instQuery('*OPC?')
            if ret[0] == '1':
                wait = False
        
    def idn(self):
        """Return response to *IDN? message"""
        return self._instQuery('*IDN?')

    def setLocal(self):
        """Set the power supply to LOCAL mode where front panel keys work again
        """

        # Not sure if this is SCPI, but it appears to be supported
        # across different instruments
        self._instWrite('SYSTem:LOCal')
    
    def setRemote(self):
        """Set the power supply to REMOTE mode where it is controlled via VISA
        """

        # Not sure if this is SCPI, but it appears to be supported
        # across different instruments
        self._instWrite('SYSTem:REMote')
    
    def setRemoteLock(self):
        """Set the power supply to REMOTE Lock mode where it is
           controlled via VISA & front panel is locked out
        """

        # Not sure if this is SCPI, but it appears to be supported
        # across different instruments
        self._instWrite('SYSTem:RWLock ON')

    def beeperOn(self):
        """Enable the system beeper for the instrument"""
        self._instWrite('SYSTem:BEEPer:STATe ON')        
        
    def beeperOff(self):
        """Disable the system beeper for the instrument"""
        self._instWrite('SYSTem:BEEPer:STATe OFF')
        
    def isOutputOn(self, channel=None):
        """Return true if the output of channel is ON, else false
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        # @@@str = 'OUTPut:STATe? {}'.format(self._chStr(self.channel))
        str = 'INSTrument:NSELect {}; OUTPut:STATe?'.format(self.channel)
        ret = self._instQuery(str)
        # @@@print("1:", ret)
        return self._onORoff(ret)
    
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
            
        # @@@str = 'OUTPut:STATe {},ON'.format(self._chStr(self.channel))
        str = 'INSTrument:NSELect {}; OUTPut:STATe ON'.format(self.channel)
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
            
        # @@@str = 'OUTPut:STATe {},OFF'.format(self._chStr(self.channel))
        str = 'INSTrument:NSELect {}; OUTPut:STATe OFF'.format(self.channel)
        self._instWrite(str)
        sleep(wait)             # give some time for PS to respond
    
    def outputOnAll(self, wait=None):
        """Turn on the output for ALL channels
        
        """

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        for chan in range(1,self._max_chan+1):
            str = 'INSTrument:NSELect {}; OUTPut:STATe ON'.format(chan)
            self._instWrite(str)
            
        sleep(wait)             # give some time for PS to respond
    
    def outputOffAll(self, wait=None):
        """Turn off the output for ALL channels
        
        """

        # If a wait time is NOT passed in, set wait to the
        # default time
        if wait is None:
            wait = self._wait

        for chan in range(1,self._max_chan+1):
            str = 'INSTrument:NSELect {}; OUTPut:STATe OFF'.format(chan)
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
            
        # @@@str = 'SOURce{}:VOLTage {}'.format(self._chanStr(self.channel), voltage)
        str = 'INSTrument:NSELect {}; SOURce:VOLTage:LEVel:IMMediate:AMPLitude {}'.format(self.channel, voltage)
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
            
        # @@@str = 'SOURce{}:CURRent {}'.format(self._chanStr(self.channel), current)
        str = 'INSTrument:NSELect {}; SOURce:CURRent:LEVel:IMMediate:AMPLitude {}'.format(self.channel, current)
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
            
        # @@@str = 'SOURce{}:VOLTage?'.format(self._chanStr(self.channel))
        str = 'INSTrument:NSELect {}; SOURce:VOLTage:LEVel:IMMediate:AMPLitude?'.format(self.channel)
        ret = self._instQuery(str)
        return float(ret)
    
    def queryCurrent(self, channel=None):
        """Return what current set value is (not the measured current,
        but the set current)
        
        channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
                    
        # @@@str = 'SOURce{}:CURRent?'.format(self._chanStr(self.channel))
        str = 'INSTrument:NSELect {}; SOURce:CURRent:LEVel:IMMediate:AMPLitude?'.format(self.channel)
        ret = self._instQuery(str)
        return float(ret)
    
    def measureVoltage(self, channel=None):
        """Read and return a voltage measurement from channel
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
                    
        str = 'INSTrument:NSELect {}; MEASure:VOLTage:DC?'.format(self.channel)
        val = self._instQuery(str)
        return float(val)
    
    def measureCurrent(self, channel=None):
        """Read and return a current measurement from channel
        
           channel - number of the channel starting at 1
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
            
        str = 'INSTrument:NSELect {}; MEASure:CURRent:DC?'.format(self.channel)
        val = self._instQuery(str)
        return float(val)
    

