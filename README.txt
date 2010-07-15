urlnorm.py
==========

Normalize a URL to a standard unicode representation

Installation
============

pip install -e git://github.com/jehiah/urlnorm.git#egg=urlnorm

Examples
========

>>> import urlnorm
>>> urlnorm.norm("http://xn--q-bga.com./u/u/../%72/l/")
u'http://q\xe9.com/u/r/l/'
