#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    print '(WARNING: importing distutils, not setuptools!)'
    from distutils.core import setup

setup(name = 'atm',
      version = '0.5',
      description = 'AWS Twill Module',
      author = 'Alex Nolley',
      author_email = 'badmit@gmail.com',
      license = 'MIT',
      
      requires = ['twill', 'boto'],

      packages = ['atm'],

      maintainer = 'Alex Nolley',
      maintainer_email = 'badmit@gmail.com',

      long_description = """\
A Twill (http://twill.idyll.org/) module for starting and stopping Amazon AWS
instances. This package automates these processes by allowing an AWS user to
associate their Amazon credentials with a name so they won't have to type in
their login information every time they want to start an instance
""",
      )
