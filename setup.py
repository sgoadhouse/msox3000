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


setup(name="dcps", 
      version='0.2',
      description='Control of DC Power Supplies through python',
      long_description=long_description,
      url='https://github.com/sgoadhouse/dcps',
      author='Stephen Goadhouse', 
      author_email="sgoadhouse@virginia.edu",
      maintainer='Stephen Goadhouse',
      maintainer_email="sgoadhouse@virginia.edu",
      license='MIT',
      keywords=['Rigol','DP800', 'PyVISA', 'VISA', 'SCPI'],
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
     install_requires=['pyvisa', 'pyvisa-py'],
     packages=["dcps"],
     include_package_data=True,
     zip_safe=False
)
