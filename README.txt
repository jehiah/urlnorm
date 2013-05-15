urlnorm.py
==========

Normalize a URL to a standard unicode representation

urlnorm normalizes a URL by:

  * lowercasing the scheme and hostname
  * converting the hostname to IDN format
  * taking out default port if present (e.g., http://www.foo.com:80/)
  * collapsing the path (./, ../, etc)
  * removing the last character in the hostname if it is '.'
  * unquoting any % escaped characters (where possible)

Installation
============

    pip install urlnorm


Example
=======

    >>> import urlnorm
    >>> urlnorm.norm("http://xn--q-bga.com./u/u/../%72/l/")
    u'http://q\xe9.com/u/r/l/'

