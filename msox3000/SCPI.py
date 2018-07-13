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
 
#---------------------------------------------------------------------------------
#  Control of HP/Agilent/Keysight MSO-X/DSO-X 3000A Oscilloscope using
#  standard SCPI commands with PyVISA
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
    """Basic class for controlling and accessing an Oscilloscope with Standard SCPI Commands"""

    def __init__(self, resource, max_chan=1, wait=0,
                     cmd_prefix = '',
                     read_termination = '',
                     write_termination = '',
                     timeout = 15000):
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
        self._timeout = timeout
        self._inst = None        

    def open(self):
        """Open a connection to the VISA device with PYVISA-py python library"""
        self._rm = visa.ResourceManager('@py')
        self._inst = self._rm.open_resource(self._resource,
                                            read_termination=self._read_termination,
                                            write_termination=self._write_termination)
        self._inst.timeout = self._timeout
        self._inst.clear()

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
        result = self._inst.query(queryStr)
        self.checkInstErrors(queryStr)
        return result
        
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
        
    # =========================================================
    # Taken from the MSO-X 3000 Programming Guide and modified to work
    # within this class ...
    # =========================================================
    # Check for instrument errors:
    # =========================================================
    def checkInstErrors(self, commandStr):

        while True:
            error_string = self._instQuery(":SYSTem:ERRor?")
            if error_string: # If there is an error string value.
                if error_string.find("+0,", 0, 3) == -1:
                    # Not "No error".
                    print("ERROR: {}, command: '{}'".format(error_string, commandStr)
                    #print "Exited because of error."
                    #sys.exit(1)
                    return True           # indicate there was an error
                else: # "No error"
                    #break
                    return False          # NO ERROR!

            else: # :SYSTem:ERRor? should always return string.
                print("ERROR: :SYSTem:ERRor? returned nothing, command: '{}'").format(commandStr)
                #print "Exited because of error."
                #sys.exit(1)

        return True           # indicate there was an error

    # =========================================================
    # Based on do_query_ieee_block() from the MSO-X 3000 Programming
    # Guide and modified to work within this class ...
    # =========================================================
    def _instQueryIEEEBlock(self, queryStr):
        if (queryStr[0] != '*'):
            queryStr = self._prefix + queryStr
        #print("QUERYIEEEBlock:",queryStr)
        result = self._inst.query_binary_values(queryStr, datatype='s')
        self.checkInstErrors(queryStr)
        return result[0]
            
    # =========================================================
    # Based on do_command_ieee_block() from the MSO-X 3000 Programming
    # Guide and modified to work within this class ...
    # =========================================================
    def _instWriteIEEEBlock(self, writeStr, values):
        if (writeStr[0] != '*'):
            writeStr = self._prefix + writeStr
        #print("WRITE:",writeStr)
        result = self._inst.write_binary_values(writeStr, values, datatype='c')
        self.checkInstErrors(writeStr)
        return result
        
    def idn(self):
        """Return response to *IDN? message"""
        return self._instQuery('*IDN?')

    def setLocal(self):
        """Set the power supply to LOCAL mode where front panel keys work again
        """

        # Not sure if this is SCPI, but it appears to be supported
        # across different instruments
        self._instWrite('SYSTem:LOCK OFF')
    
    def setRemote(self):
        """Set the power supply to REMOTE mode where it is controlled via VISA
        """

        # Not sure if this is SCPI, but it appears to be supported
        # across different instruments
        self._instWrite('SYSTem:LOCK ON')
    
    def setRemoteLock(self):
        """Set the power supply to REMOTE Lock mode where it is
           controlled via VISA & front panel is locked out
        """

        # Not sure if this is SCPI, but it appears to be supported
        # across different instruments
        self._instWrite('SYSTem:LOCK ON')

    def beeperOn(self):
        """Enable the system beeper for the instrument"""
        # no beeper to turn off, so make it do nothing
        pass
        
    def beeperOff(self):
        """Disable the system beeper for the instrument"""
        # no beeper to turn off, so make it do nothing
        pass

    def isOutputOnOLD(self, channel=None):
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
    
    def outputOnOLD(self, channel=None, wait=None):
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
    
    def outputOffOLD(self, channel=None, wait=None):
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
    
    def outputOnAllOLD(self, wait=None):
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
    
    def outputOffAllOLD(self, wait=None):
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
    
    

