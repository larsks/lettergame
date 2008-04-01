#!/usr/bin/python

from distutils.core import setup

setup(name = "lettergame",
  version = "1",
  description = "A silly letter game for toddlers.",
  author = "Lars Kellogg-Stedman",
  author_email = "lars@oddbit.com",
  url = "http://code.google.com/p/lettergame/",
  packages = [
    'lettergame',
  ],
  package_dir = { '': 'lib'},
  scripts = [
    'scripts/lettergame',
  ],
  package_data={'lettergame': [
    'sounds/*/*',
    'images/*',
    ]}
)

