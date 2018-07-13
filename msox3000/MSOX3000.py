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
        super(MSOX3000, self).__init__(resource, max_chan=4, wait=wait,
                                       cmd_prefix=':',
                                       read_strip='\n',
                                       read_termination='',
                                       write_termination='\n'
                                      )


    # =========================================================
    # Based on the screen image download example from the MSO-X 3000 Programming
    # Guide and modified to work within this class ...
    # =========================================================
    def hardcopy(self, filename):
        """ Download the screen image to the given filename. """

        self._instWrite("HARDcopy:INKSaver OFF")
        scrImage = self._instQueryIEEEBlock("DISPlay:DATA? PNG, COLor")

        # Save display data values to file.
        f = open(filename, "wb")
        f.write(scrImage)
        f.close()

    # =========================================================
    # Based on the Waveform data download example from the MSO-X 3000 Programming
    # Guide and modified to work within this class ...
    # =========================================================
    def waveform(self, filename, channel=None):
        """ Download the Waveform Data of a particular Channel and saved to the given filename as a CSV file. """

        DEBUG = False
        import csv

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
        
        # Download waveform data.
        # Set the waveform points mode.
        self._instWrite("WAVeform:POINts:MODE RAW")
        if DEBUG:
            qresult = self._instQuery("WAVeform:POINts:MODE?")
            print( "Waveform points mode: {}".format(qresult) )

        # Set the number of waveform points to fetch - make this a parameter perhaps
        #@@@#self._instWrite("WAVeform:POINts 10240")
        #@@@#self._instWrite("WAVeform:POINts 62500")
        if DEBUG:
            qresult = self._instQuery("WAVeform:POINts?")
            print( "Waveform points available: {}".format(qresult) )

        # Set the waveform source.
        self._instWrite("WAVeform:SOURce {}".format(self._channelStr(self.channel)))
        if DEBUG:
            qresult = self._instQuery("WAVeform:SOURce?")
            print( "Waveform source: {}".format(qresult) )

        # Choose the format of the data returned:
        self._instWrite("WAVeform:FORMat BYTE")
        if DEBUG:
            print( "Waveform format: {}".format(self._instQuery("WAVeform:FORMat?")) )

        if DEBUG:
            # Display the waveform settings from preamble:
            wav_form_dict = {
                0 : "BYTE",
                1 : "WORD",
                4 : "ASCii", }

            acq_type_dict = {
                0 : "NORMal",
                1 : "PEAK",
                2 : "AVERage",
                3 : "HRESolution",
            }

            (
                wav_form_f,
                acq_type_f,
                wfmpts_f,
                avgcnt_f,
                x_increment,
                x_origin,
                x_reference_f,
                y_increment,
                y_origin,
                y_reference_f
            ) = self._instQueryNumbers("WAVeform:PREamble?")

            ## convert the numbers that are meant to be integers
            (
                wav_form,
                acq_type,
                wfmpts,
                avgcnt,
                x_reference,
                y_reference
            ) = list(map(int,         (
                wav_form_f,
                acq_type_f,
                wfmpts_f,
                avgcnt_f,
                x_reference_f,
                y_reference_f
            )))


            print( "Waveform format: {}".format(wav_form_dict[(wav_form)]) )
            print( "Acquire type: {}".format(acq_type_dict[(acq_type)]) )
            print( "Waveform points desired: {:d}".format((wfmpts)) )
            print( "Waveform average count: {:d}".format((avgcnt)) )
            print( "Waveform X increment: {:1.12f}".format(x_increment) )
            print( "Waveform X origin: {:1.9f}".format(x_origin) )
            print( "Waveform X reference: {:d}".format((x_reference)) ) # Always 0. 
            print( "Waveform Y increment: {:f}".format(y_increment) )
            print( "Waveform Y origin: {:f}".format(y_origin) )
            print( "Waveform Y reference: {:d}".format((y_reference)) ) # Always 125.

        # Get numeric values for later calculations.
        x_increment = self._instQueryNumber("WAVeform:XINCrement?")
        x_origin = self._instQueryNumber("WAVeform:XORigin?")
        y_increment = self._instQueryNumber("WAVeform:YINCrement?")
        y_origin = self._instQueryNumber("WAVeform:YORigin?")
        y_reference = self._instQueryNumber("WAVeform:YREFerence?")

        # Get the waveform data.
        data_bytes = self._instQueryIEEEBlock("WAVeform:DATA?")
        nLength = len(data_bytes)
        print( "Number of data values: {:d}".format(nLength) )

        # Open file for output.
        myFile = open(filename, 'w')
        with myFile:
            writer = csv.writer(myFile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(['Time (s)', 'Voltage (V)'])

            # Output waveform data in CSV format.
            for i in range(0, nLength - 1):
                time_val = x_origin + (i * x_increment)
                voltage = (data_bytes[i] - y_reference) * y_increment + y_origin
                writer.writerow([time_val, voltage])

        print( "Waveform format BYTE data written to {}.".format(filename) )


    def _readDVM(self, mode, channel=None):
        """ Read the DVM data of desired channel and return the value. """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # First check if DVM is enabled
        en = self._instQuery("DVM:ENABle?")
        if (not self._1OR0(en)):
            # It is not enabled, so enable it
            self._instWrite("DVM:ENABLE ON")

        # Next check if desired DVM channel is the source, if not switch it
        #
        # NOTE: doing it this way so as to not possibly break the
        # moving average since do not know if buffers are cleared when
        # the SOURCE command is sent even if the channel does not
        # change.
        src = self._instQuery("DVM:SOURce?")
        #print("Source: {}".format(src))
        if (self._chanNumber(src) != self.channel):
            # Different channel number so switch it
            #print("Switching to {}".format(self.channel))
            self._instWrite("DVM:SOURce {}".format(self._channelStr(self.channel)))

        # Select the desired DVM mode
        self._instWrite("DVM:MODE {}".format(mode))

        # Read value until get one < +9.9E+37 (per programming guide suggestion)
        val = 9.9E+37
        while (val >= 9.9E+37):
            val = self._instQueryNumber("DVM:CURRent?")

        # if mode is frequency, return the 5-digit frequency instead
        if (mode == "FREQ"):
            val = self._instQueryNumber("DVM:FREQ?")
            
        return val
        
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
