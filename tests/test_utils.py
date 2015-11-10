"""
Test utils module.
"""

from os import path
import unittest
import logging

from aws_scripts.utils import mkdir, Opener, opener

from __init__ import TestBase, get_testfile
log = logging.getLogger(__name__)


class Args(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestOpener(TestBase):

    def setUp(self):
        with open(get_testfile('lorem.txt')) as f:
            self.firstline = f.next()

    def test01(self):
        for suffix in ['txt', 'gz', 'bz2']:
            fn = get_testfile('lorem.' + suffix)
            fobj = opener(fn)
            self.assertEqual(fobj.next(), self.firstline)

    def test02(self):
        for suffix in ['txt', 'gz', 'bz2']:
            fn = get_testfile('lorem.' + suffix)
            fobj = opener(fn, 'r')
            self.assertEqual(fobj.next(), self.firstline)
