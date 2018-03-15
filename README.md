# dcps
Control of DC Power Supplies through python

This is intended to be a generic package to control various DC power
supplies using various access methods with a common API. For now, this
only supports the Rigol DP832A DC Power Supply through pyVISA and the
SCPI command set. This should work with all Rigol DP8xx power supplies
although it is only tested with the DP832A.

As new power supplies are added, they should each have their own sub-package.


# Installation
You need to install the pyvisa and pyvisa-py packages. 

To install the dcps package, run the command:

```
python setup.py install
```

Alternatively, can add a path to this package to the environment
variable PYTHONPATH or even add the path to it at the start of your
python script. Use your favorite web search engine to find out more
details.

Even better, dcps is now on PyPi, so you can simply use the following
and the required depedancies should get installed for you:

```
pip install dcps
```

## Requirements
* [python](http://www.python.org/) [Works with 2.7+ and 3+]
* [pyvisa 1.9](https://pyvisa.readthedocs.io/en/stable/)
* [pyvisa-py 0.2](https://pyvisa-py.readthedocs.io/en/latest/)

With the use of pyvisa-py, should not have to install the National
Instruments NIVA driver.

# WARNING!
Be *really* careful since you are controlling a power supply that may be
connected to something that does not like to go to 33V when you
meant 3.3V and it may express its displeasure by exploding all over
the place. So be sure to do ALL testing without a device connected,
as much as possible, and make use of the protections built into the
power supply. For example, you can set voltage and current limits that
the power supply will obey and ignore requests by these commands to go
outside the allowable ranges. There are even SCPI commands to set
these limits, but they are not in this class because I think it is
safer that they be set manually. Of course, you can easily add those
commands and do it programatically if you like living dangerously.

## Usage
The code is a very basic class for controlling and accessing the Rigol
DP832A and other power supplies in the DP800 family. Before running
any example, be extra sure that the power supply is disconnected from
any device in case voltsges unexpectedly go to unexpected values.

If running the examples embedded in the individual package source
files, be sure to set the resource string or VISA descriptor of your
particular device. You can either set an environment variable,
DP800_IP or change the code where the RigolDP800() is being
instantiated.

```python
# Lookup environment variable DP800_IP and use it as the resource
# name or use the TCPIP0 string if the environment variable does
# not exist
from dcps import RigolDP800
from os import environ
resource = environ.get('DP800_IP', 'TCPIP0::172.16.2.13::INSTR')

# create your visa instrument
rigol = RigolDP800(resource)
rigol.open()

# access channel 1
chan = 1

# Query the voltage/current limits of the power supply
print('Ch. {} Settings: {:6.4f} V  {:6.4f} A'.
         format(chan, rigol.queryVoltage(channel=chan),
                    rigol.queryCurrent(channel=chan)))

# Enable output of channel
rigol.outputOn(channel=chan)

# Measure actual voltage and current
print('{:6.4f} V'.format(rigol.measureVoltage(channel=chan)))
print('{:6.4f} A'.format(rigol.measureCurrent(channel=chan)))

# change voltage output to 2.7V
rigol.setVoltage(2.7, channel=chan)

# turn off the channel
rigol.outputOff(channel=chan)

# return to LOCAL mode
rigol.setLocal()

rigol.close()
```

## Taking it Further
This implements a small subset of available commands. For information
on what is possible for the Rigol DP8xx, see the [Rigol DP800 Programming Guide](http://beyondmeasure.rigoltech.com/acton/attachment/1579/f-03a1/1/-/-/-/-/DP800%20Programming%20Guide.pdf)


## Contact
Please send bug reports or feedback to Stephen Goadhouse

