# -*- coding: utf-8 -*-

#from distutils.core import setup
from setuptools import setup

long_description=u'''\
Overview
--------

This is intended to be a generic package to control various DC power
supplies using various access methods with a common API. For now, this
only supports the Rigol DP832A DC Power Supply through pyVISA and the
SCPI command set. This should work with all Rigol DP8xx power supplies
although it is only tested with the DP832A.

As new power supplies are added, they should each have their own sub-package.

Installation
------------

You need to install the pyvisa and pyvisa-py packages. 

To install the dcps package, run the command ::

   python setup.py install

Alternatively, can add a path to this package to the environment
variable PYTHONPATH or even add the path to it at the start of your
python script. Use your favorite web search engine to find out more
details.

Usage
-----

First you need to create your visa instrument. ::

    # Lookup environment variable DP800_IP and use it as the resource
    # name or use the TCPIP0 string if the environment variable does
    # not exist
    from dcps import RigolDP800
    from os import environ
    resource = environ.get('DP800_IP', 'TCPIP0::172.16.2.13::INSTR')
    rigol = RigolDP800(resource)
    rigol.open()

    chan = 1  # access channel 1

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


Contact
-------

Please send bug reports or feedback to Stephen Goadhouse

'''


def readme():
    with open('README.md') as f:
        return f.read()

setup(name="dcps", 
      version='0.1',
      description='Control of DC Power Supplies through python',
      long_description=readme(),
      url='https://github.com/sgoadhouse/dcps',
      author='Stephen Goadhouse', 
      author_email="sgoadhouse@virginia.edu",
      maintainer='Stephen Goadhouse',
      maintainer_email="sgoadhouse@virginia.edu",
      license='MIT',
      keywords=['Rigol','DP800', 'PyVISA', 'VISA', 'SCPI'],
      classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'], 
     install_requires=['pyvisa', 'pyvisa-py'],
     packages=["dcps"],
     include_package_data=True,
     zip_safe=False
)
