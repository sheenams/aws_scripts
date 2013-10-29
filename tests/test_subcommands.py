"""
Test subcommands.
"""

import logging

from aws_scripts.scripts.main import main
from __init__ import TestCaseSuppressOutput, TestBase

log = logging.getLogger(__name__)

class TestTemplate(TestCaseSuppressOutput, TestBase):

    def testExit01(self):
        self.assertRaises(SystemExit, main, ['notacommand'])

    def testExit02(self):
        self.assertRaises(SystemExit, main, ['-h'])

    def test01(self):
        main(['template', 'infile', 'outfile', '--monkey-type', 'macaque'])
