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
from datetime import datetime
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
    # Based on the save oscilloscope setup example from the MSO-X 3000 Programming
    # Guide and modified to work within this class ...
    # =========================================================
    def setupSave(self, filename):
        """ Fetch the oscilloscope setup and save to a file with given filename. """

        oscopeSetup = self._instQueryIEEEBlock("SYSTem:SETup?")

        # Save setup to file.
        f = open(filename, "wb")
        f.write(oscopeSetup)
        f.close()

        print('Oscilloscope Setup bytes saved: {} to "{}"'.format(len(oscopeSetup),filename))


    # =========================================================
    # Based on the loading a previous setup example from the MSO-X 3000 Programming
    # Guide and modified to work within this class ...
    # =========================================================
    def setupLoad(self, filename):
        """ Restore the oscilloscope setup from file with given filename. """

        # Load setup from file.
        f = open(filename, "rb")
        oscopeSetup = f.read()
        f.close()

        print('Oscilloscope Setup bytes loaded: {} from "{}"'.format(len(oscopeSetup),filename))

        self._instWriteIEEEBlock("SYSTem:SETup ", oscopeSetup)  


    def setupAutoscale(self, channel=None):
        """ Autoscale desired channel. """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel
                    
        self._instWrite("AUToscale {}".format(self._channelStr(self.channel)))


    def measureStatistics(self):
        """Returns an array of dictionaries from the current statistics window.

        The definition of the returned dictionary can be easily gleaned
        from the code below.
        """

        # turn on the statistics display
        self._instWrite("MEASure:STATistics:DISPlay ON")

        # tell Results? return all values (as opposed to just one of them)
        self._instWrite("MEASure:STATistics ON")

        # create a list of the return values, which are seperated by a comma
        statFlat = self._instQuery("MEASure:RESults?").split(',')

        # convert the flat list into a two-dimentional matrix with seven columns per row
        statMat = [statFlat[i:i+7] for i in range(0,len(statFlat),7)]

        # convert each row into a dictionary, while converting text strings into numbers
        stats = []
        for stat in statMat:
            stats.append({'label':stat[0],
                          'CURR':float(stat[1]),   # Current Value
                          'MIN':float(stat[2]),    # Minimum Value
                          'MAX':float(stat[3]),    # Maximum Value
                          'MEAN':float(stat[4]),   # Average/Mean Value
                          'STDD':float(stat[5]),   # Standard Deviation
                          'COUN':int(stat[6])      # Count of measurements
                          })

        # return the result in an array of dictionaries
        return stats
    
    def _measure(self, mode, para=None, channel=None, install=False):
        """Read and return a measurement of type mode from channel
        
           para - parameters to be passed to command

           channel - number of the channel to be measured starting at 1 

           install - if True, adds measurement to the statistics display
        """

        # If a channel number is passed in, make it the
        # current channel
        if channel is not None:
            self.channel = channel

        # Next check if desired channel is the source, if not switch it
        #
        # NOTE: doing it this way so as to not possibly break the
        # moving average since do not know if buffers are cleared when
        # the SOURCE command is sent even if the channel does not
        # change.
        src = self._instQuery("MEASure:SOURce?")
        #print("Source: {}".format(src))
        if (self._chanNumber(src) != self.channel):
            # Different channel number so switch it
            #print("Switching to {}".format(self.channel))
            self._instWrite("MEASure:SOURce {}".format(self._channelStr(self.channel)))

        if (para):
            # Need to add parameters to the write and query strings
            strWr = "MEASure:{} {}".format(mode, para)
            strQu = "MEASure:{}? {}".format(mode, para)
        else:
            strWr = "MEASure:{}".format(mode)
            strQu = "MEASure:{}?".format(mode)
                
        if (install):
            # If desire to install the measurement, make sure the
            # statistics display is on and then use the command form of
            # the measurement to install the measurement.
            self._instWrite("MEASure:STATistics:DISPlay ON")
            self._instWrite(strWr)

        # query the measurement (do not have to install to query it)
        val = self._instQuery(strQu)

        return float(val)

    def measureBitRate(self, channel=None, install=False):
        """Measure and return the bit rate measurement.

        This measurement is defined as: 'measures all positive and
        negative pulse widths on the waveform, takes the minimum value
        found of either width type and inverts that minimum width to
        give a value in Hertz'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("BRATe", channel=channel, install=install)
    
    def measureBurstWidth(self, channel=None, install=False):
        """Measure and return the bit rate measurement.

        This measurement is defined as: 'the width of the burst on the
        screen.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.
        
        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("BWIDth", channel=channel, install=install)
    
    def measureCounterFrequency(self, channel=None, install=False):
        """Measure and return the counter frequency

        This measurement is defined as: 'the counter frequency.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - issues if install, so this paramter is ignored
        """

        # NOTE: The programmer's guide suggests sending a :MEASURE:CLEAR
        # first because if COUNTER is installed for ANY channel, this
        # measurement will fail. Note doing the CLEAR, but if COUNTER
        # gets installed, this will fail until it gets manually CLEARed.
        
        return self._measure("COUNter", channel=channel, install=False)
    
    def measurePosDutyCycle(self, channel=None, install=False):
        """Measure and return the positive duty cycle

        This measurement is defined as: 'The value returned for the duty
        cycle is the ratio of the positive pulse width to the
        period. The positive pulse width and the period of the specified
        signal are measured, then the duty cycle is calculated with the
        following formula:

        duty cycle = (+pulse width/period)*100'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("DUTYcycle", channel=channel, install=install)
    
    def measureFallTime(self, channel=None, install=False):
        """Measure and return the fall time

        This measurement is defined as: 'the fall time of the displayed
        falling (negative-going) edge closest to the trigger
        reference. The fall time is determined by measuring the time at
        the upper threshold of the falling edge, then measuring the time
        at the lower threshold of the falling edge, and calculating the
        fall time with the following formula:

        fall time = time at lower threshold - time at upper threshold'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("FALLtime", channel=channel, install=install)
    
    def measureRiseTime(self, channel=None, install=False):
        """Measure and return the rise time

        This measurement is defined as: 'the rise time of the displayed
        rising (positive-going) edge closest to the trigger
        reference. For maximum measurement accuracy, set the sweep speed
        as fast as possible while leaving the leading edge of the
        waveform on the display. The rise time is determined by
        measuring the time at the lower threshold of the rising edge and
        the time at the upper threshold of the rising edge, then
        calculating the rise time with the following formula:

        rise time = time at upper threshold - time at lower threshold'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("RISetime", channel=channel, install=install)
    
    def measureFrequency(self, channel=None, install=False):
        """Measure and return the frequency of cycle on screen

        This measurement is defined as: 'the frequency of the cycle on
        the screen closest to the trigger reference.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("FREQ", channel=channel, install=install)
    
    def measureNegDutyCycle(self, channel=None, install=False):
        """Measure and return the negative duty cycle

        This measurement is defined as: 'The value returned for the duty
        cycle is the ratio of the negative pulse width to the
        period. The negative pulse width and the period of the specified
        signal are measured, then the duty cycle is calculated with the
        following formula:

        -duty cycle = (-pulse width/period)*100'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("NDUTy", channel=channel, install=install)
    
    def measureFallEdgeCount(self, channel=None, install=False):
        """Measure and return the on-screen falling edge count

        This measurement is defined as: 'the on-screen falling edge
        count'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("NEDGes", channel=channel, install=install)
    
    def measureFallPulseCount(self, channel=None, install=False):
        """Measure and return the on-screen falling pulse count

        This measurement is defined as: 'the on-screen falling pulse
        count'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("NPULses", channel=channel, install=install)
    
    def measureNegPulseWidth(self, channel=None, install=False):
        """Measure and return the on-screen falling/negative pulse width

        This measurement is defined as: 'the width of the negative pulse
        on the screen closest to the trigger reference using the
        midpoint between the upper and lower thresholds.

        FOR the negative pulse closest to the trigger point:

        width = (time at trailing rising edge - time at leading falling edge)'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("NWIDth", channel=channel, install=install)
    
    def measureOvershoot(self, channel=None, install=False):
        """Measure and return the on-screen voltage overshoot in percent

        This measurement is defined as: 'the overshoot of the edge
        closest to the trigger reference, displayed on the screen. The
        method used to determine overshoot is to make three different
        vertical value measurements: Vtop, Vbase, and either Vmax or
        Vmin, depending on whether the edge is rising or falling.

        For a rising edge:

        overshoot = ((Vmax-Vtop) / (Vtop-Vbase)) x 100

        For a falling edge:

        overshoot = ((Vbase-Vmin) / (Vtop-Vbase)) x 100

        Vtop and Vbase are taken from the normal histogram of all
        waveform vertical values. The extremum of Vmax or Vmin is taken
        from the waveform interval right after the chosen edge, halfway
        to the next edge. This more restricted definition is used
        instead of the normal one, because it is conceivable that a
        signal may have more preshoot than overshoot, and the normal
        extremum would then be dominated by the preshoot of the
        following edge.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("OVERshoot", channel=channel, install=install)
    
    def measurePreshoot(self, channel=None, install=False):
        """Measure and return the on-screen voltage preshoot in percent

        This measurement is defined as: 'the preshoot of the edge
        closest to the trigger, displayed on the screen. The method used
        to determine preshoot is to make three different vertical value
        measurements: Vtop, Vbase, and either Vmin or Vmax, depending on
        whether the edge is rising or falling.

        For a rising edge:

        preshoot = ((Vmin-Vbase) / (Vtop-Vbase)) x 100

        For a falling edge:

        preshoot = ((Vmax-Vtop) / (Vtop-Vbase)) x 100

        Vtop and Vbase are taken from the normal histogram of all
        waveform vertical values. The extremum of Vmax or Vmin is taken
        from the waveform interval right before the chosen edge, halfway
        back to the previous edge. This more restricted definition is
        used instead of the normal one, because it is likely that a
        signal may have more overshoot than preshoot, and the normal
        extremum would then be dominated by the overshoot of the
        preceding edge.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("PREShoot", channel=channel, install=install)
    
    def measureRiseEdgeCount(self, channel=None, install=False):
        """Measure and return the on-screen rising edge count

        This measurement is defined as: 'the on-screen rising edge
        count'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("PEDGes", channel=channel, install=install)
    
    def measureRisePulseCount(self, channel=None, install=False):
        """Measure and return the on-screen rising pulse count

        This measurement is defined as: 'the on-screen rising pulse
        count'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("PPULses", channel=channel, install=install)
    
    def measurePosPulseWidth(self, channel=None, install=False):
        """Measure and return the on-screen falling/positive pulse width

        This measurement is defined as: 'the width of the displayed
        positive pulse closest to the trigger reference. Pulse width is
        measured at the midpoint of the upper and lower thresholds.

        IF the edge on the screen closest to the trigger is falling:

        THEN width = (time at trailing falling edge - time at leading rising edge)

        ELSE width = (time at leading falling edge - time at leading rising edge)'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("PWIDth", channel=channel, install=install)
    
    def measurePeriod(self, channel=None, install=False):
        """Measure and return the on-screen period

        This measurement is defined as: 'the period of the cycle closest
        to the trigger reference on the screen. The period is measured
        at the midpoint of the upper and lower thresholds.

        IF the edge closest to the trigger reference on screen is rising:

        THEN period = (time at trailing rising edge - time at leading rising edge)

        ELSE period = (time at trailing falling edge - time at leading falling edge)'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("PERiod", channel=channel, install=install)
    
    def measureVoltAmplitude(self, channel=None, install=False):
        """Measure and return the vertical amplitude of the signal

        This measurement is defined as: 'the vertical amplitude of the
        waveform. To determine the amplitude, the instrument measures
        Vtop and Vbase, then calculates the amplitude as follows:

        vertical amplitude = Vtop - Vbase'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VAMPlitude", channel=channel, install=install)
    
    def measureVoltAverage(self, channel=None, install=False):
        """Measure and return the Average Voltage measurement.

        This measurement is defined as: 'average value of an integral
        number of periods of the signal. If at least three edges are not
        present, the oscilloscope averages all data points.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VAVerage", para="DISPlay", channel=channel, install=install)
    
    def measureVoltRMS(self, channel=None, install=False):
        """Measure and return the DC RMS Voltage measurement.

        This measurement is defined as: 'the dc RMS value of the
        selected waveform. The dc RMS value is measured on an integral
        number of periods of the displayed signal. If at least three
        edges are not present, the oscilloscope computes the RMS value
        on all displayed data points.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VRMS", para="DISPlay", channel=channel, install=install)
    
    def measureVoltBase(self, channel=None, install=False):
        """Measure and return the Voltage base measurement.

        This measurement is defined as: 'the vertical value at the base
        of the waveform. The base value of a pulse is normally not the
        same as the minimum value.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VBASe", channel=channel, install=install)
    
    def measureVoltTop(self, channel=None, install=False):
        """Measure and return the Voltage Top measurement.

        This measurement is defined as: 'the vertical value at the top
        of the waveform. The top value of the pulse is normally not the
        same as the maximum value.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VTOP", channel=channel, install=install)
    
    def measureVoltMax(self, channel=None, install=False):
        """Measure and return the Maximum Voltage measurement.

        This measurement is defined as: 'the maximum vertical value
        present on the selected waveform.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VMAX", channel=channel, install=install)
    

    def measureVoltMin(self, channel=None, install=False):
        """Measure and return the Minimum Voltage measurement.

        This measurement is defined as: 'the minimum vertical value
        present on the selected waveform.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VMIN", channel=channel, install=install)
    

    def measureVoltPP(self, channel=None, install=False):
        """Measure and return the voltage peak-to-peak measurement.

        This measurement is defined as: 'the maximum and minimum
        vertical value for the selected source, then calculates the
        vertical peak-to-peak value and returns that value. The
        peak-to-peak value (Vpp) is calculated with the following
        formula:

        Vpp = Vmax - Vmin

        Vmax and Vmin are the vertical maximum and minimum values
        present on the selected source.'

        If the returned value is >= SCPI.OverRange, then no valid value
        could be measured.

        channel: channel number to be measured - default channel for
        future readings

        install - if True, adds measurement to the statistics display
        """

        return self._measure("VPP", channel=channel, install=install)
    

    def _readDVM(self, mode, channel=None, timeout=None):
        """Read the DVM data of desired channel and return the value. 

        channel: channel number to set to DVM mode and return its
        reading - becomes the default channel for future readings

        timeout: if None, no timeout, otherwise, time-out in seconds
        waiting for a valid number
        """

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
        startTime = datetime.now()
        val = SCPI.OverRange
        while (val >= SCPI.OverRange):
            duration = datetime.now() - startTime
            if (timeout is not None and duration.total_seconds() >= timeout):
                # if timeout is a value and have been waiting that
                # many seconds for a valid DVM value, stop waiting and
                # return this SCPI.OverRange number.
                break
            
            val = self._instQueryNumber("DVM:CURRent?")

        # if mode is frequency, read and return the 5-digit frequency instead
        if (mode == "FREQ"):
            val = self._instQueryNumber("DVM:FREQ?")
            
        return val

    def measureDVMacrms(self, channel=None, timeout=None):
        """Measure and return the AC RMS reading of channel using DVM
        mode.

        AC RMS is defined as 'the root-mean-square value of the acquired
        data, with the DC component removed.'

        channel: channel number to set to DVM mode and return its
        reading - becomes the default channel for future readings

        timeout: if None, no timeout, otherwise, time-out in seconds
        waiting for a valid number - if timeout, returns SCPI.OverRange
        """

        return self._readDVM("ACRM", channel, timeout)
    
    def measureDVMdc(self, channel=None, timeout=None):
        """ Measure and return the DC reading of channel using DVM mode. 
        
        DC is defined as 'the DC value of the acquired data.'

        channel: channel number to set to DVM mode and return its
        reading - becomes the default channel for future readings

        timeout: if None, no timeout, otherwise, time-out in seconds
        waiting for a valid number - if timeout, returns SCPI.OverRange
        """

        return self._readDVM("DC", channel, timeout)
    
    def measureDVMdcrms(self, channel=None, timeout=None):
        """ Measure and return the DC RMS reading of channel using DVM mode. 
        
        DC RMS is defined as 'the root-mean-square value of the acquired data.'

        channel: channel number to set to DVM mode and return its
        reading - becomes the default channel for future readings

        timeout: if None, no timeout, otherwise, time-out in seconds
        waiting for a valid number - if timeout, returns SCPI.OverRange
        """

        return self._readDVM("DCRM", channel, timeout)
    
    def measureDVMfreq(self, channel=None, timeout=3):
        """ Measure and return the FREQ reading of channel using DVM mode. 
        
        FREQ is defined as 'the frequency counter measurement.'

        channel: channel number to set to DVM mode and return its
        reading - becomes the default channel for future readings

        timeout: if None, no timeout, otherwise, time-out in seconds
        waiting for a valid number - if timeout, returns SCPI.OverRange

        NOTE: If the signal is not periodic, this call will block until
        a frequency is measured, unless a timeout value is given.
        """

        return self._readDVM("FREQ", channel, timeout)
    

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
