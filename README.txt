urlnorm.py
==========

Normalize a URL to a standard unicode representation

This will convert to domains to IDN format, lowercase the domain and protocol, properly unescape path, query and fragment component, and collapse redundant path segments.

Installation
============

pip install urlnorm

or to install from source

pip install -e git://github.com/jehiah/urlnorm.git#egg=urlnorm

Examples
========

>>> import urlnorm
>>> urlnorm.norm("http://xn--q-bga.com./u/u/../%72/l/")
u'http://q\xe9.com/u/r/l/'
