# -*- coding: utf-8 -*-

#from distutils.core import setup
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(name="msox3000", 
      version='0.2',
      description='Control of HP/Agilent/Keysight MSO-X/DSO-X 3000A Oscilloscope through python via PyVisa',
      long_description=long_description,
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
     install_requires=['pyvisa', 'pyvisa-py', 'argparse', 'QuantiPhy'],
     packages=["msox3000"],
     include_package_data=True,
     zip_safe=False
)
