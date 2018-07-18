# msox3000
Control of HP/Agilent/Keysight MSO-X/DSO-X 3000A Oscilloscope through python via PyVisa

Using my previous work on dcps as a guide, this is intended to be a
generic package to control various Oscilloscopes. However, it is
expected that very few oscilloscopes share the same commands so start
off as a python Class specifically for the MSO-X/DSO-X 3000A
Oscilloscope. So will start targeted toward that family of
oscilloscope with a common SCPI.py Class. If it proves useful for
other oscilloscopes, then will create a new project but at least this
one would have started with that in mind.

It may also work on the MSO-X/DSO-X 2000A oscilloscope
but I have not looked into the differences ot know for sure. Try it
out and let me know.

Like dcps, this will use the brilliant PyVISA python package along
with the PyVisa-PY access mode which eliminates the need for the (very
buggy) VISA library to be installed on your computer. 

# Installation
You need to install the pyvisa and pyvisa-py packages. 

To install the msox3000 package, run the command:

```
python setup.py install
```

Alternatively, can add a path to this package to the environment
variable PYTHONPATH or even add the path to it at the start of your
python script. Use your favorite web search engine to find out more
details.

Even better, msox3000 is on PyPi. So
you can simply use the following and the required depedancies should
get installed for you:

```
pip install msox3000
```

## Requirements
* [python](http://www.python.org/) [Works with 2.7+ and 3+]
* [pyvisa 1.9](https://pyvisa.readthedocs.io/en/stable/)
* [pyvisa-py 0.2](https://pyvisa-py.readthedocs.io/en/latest/) 
* [quantiphy 2.3.0](http://quantiphy.readthedocs.io/en/stable/) 

With the use of pyvisa-py, should not have to install the National
Instruments NIVA driver.

## Usage
The code is a very basic class for controlling and accessing the
supported oscilloscopes.

If running the examples embedded in the individual package source
files, be sure to edit the resource string or VISA descriptor of your
particular device. For MSOX3000.py, you can also set an environment
variable, MSOX3000\_IP to the desired resource string before running the
code. 

```python
# Lookup environment variable MSOX3000_IP and use it as the resource
# name or use the TCPIP0 string if the environment variable does
# not exist
from msox3000 import MSOX3000
from os import environ
resource = environ.get('MSOX3000_IP', 'TCPIP0::172.16.2.13::INSTR')

# create your visa instrument
instr = MSOX3000(resource)
instr.open()

# set to channel 1
#
# NOTE: can pass channel to each method or just set it
# once and it becomes the default for all following calls. If pass the
# channel to a Class method call, it will become the default for
# following method calls.
instr.channel = 1

# Enable output of channel, if it is not already enabled
if not instr.isOutputOn():
    instr.outputOn()

# Install measurements to display in statistics display and also
# return their current values here
print('Ch. {} Settings: {:6.4e} V  PW {:6.4e} s\n'.
          format(instr.channel, instr.measureVoltAverage(install=True),
                     instr.measurePosPulseWidth(install=True)))

# Add an annotation to the screen before hardcopy
instr._instWrite("DISPlay:ANN ON")
instr._instWrite('DISPlay:ANN:TEXT "{}\\n{} {}"'.format('Example of Annotation','for Channel',instr.channel))
instr._instWrite("DISPlay:ANN:COLor CH{}".format(instr.channel))

# Change label of the channel to "MySig"
instr._instWrite('CHAN{}:LABel "MySig"'.format(instr.channel))
instr._instWrite('DISPlay:LABel ON')

# Make sure the statistics display is showing
instr._instWrite("SYSTem:MENU MEASure")
instr._instWrite("MEASure:STATistics:DISPlay ON")

## Save a hardcopy of the screen to file 'outfile.png'
instr.hardcopy('outfile.png')

# Change label back to the default
instr._instWrite('CHAN{}:LABel "{}"'.format(instr.channel, instr.channel))
instr._instWrite('DISPlay:LABel OFF')

# Turn off the annotation
instr._instWrite("DISPlay:ANN OFF")
    
# turn off the channel
instr.outputOff()

# return to LOCAL mode
instr.setLocal()

instr.close()
```

## Taking it Further
This implements a small subset of available commands.

For information on what is possible for the HP/Agilent/Keysight MSO-X/DSO-X
3000A, see the
[Keysight InfiniiVision
3000 X-Series Oscilloscopes Programming Guide](https://www.keysight.com/upload/cmc_upload/All/3000_series_prog_guide.pdf)

For what is possible with general instruments that adhere to the
IEEE 488 SCPI specification, like the MSO-X 3000A, see the
[SCPI 1999 Specification](http://www.ivifoundation.org/docs/scpi-99.pdf)
and the
[SCPI Wikipedia](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments) entry.

## Contact
Please send bug reports or feedback to Stephen Goadhouse

