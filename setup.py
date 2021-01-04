# -*- coding: utf-8 -*-

#from distutils.core import setup
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="msox3000", 
      version='0.4.0',
      description='Control of HP/Agilent/Keysight MSO-X/DSO-X 3000A Oscilloscope through python via PyVisa',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/sgoadhouse/msox3000',
      author='Stephen Goadhouse', 
      author_email="sgoadhouse@virginia.edu",
      maintainer='Stephen Goadhouse',
      maintainer_email="sgoadhouse@virginia.edu",
      license='MIT',
      keywords=['HP', 'Agilent', 'Keysight', 'MSO3000', 'MSOX3000', 'DSO3000', 'DSOX3000' 'PyVISA', 'VISA', 'SCPI', 'INSTRUMENT'],
      classifiers=[
        'Development Status :: 4 - Beta',
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
     install_requires=[
         'pyvisa>=1.11.3',
         'pyvisa-py>=0.5.1',
         'argparse',
         'QuantiPhy>=2.3.0'
     ],
     python_requires='>=3.6',
     packages=setuptools.find_packages(),
     include_package_data=True,
     zip_safe=False
)
