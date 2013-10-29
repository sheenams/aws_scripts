======================================
AWS Scripts
======================================

Scripts to push and pull data from Glacier using boto

.. contents:: Table of Contents


dependencies
============

* Python 2.7.x
* Tested on Linux and OS X.
* boto

installation
============

Clone the project from the git repository to create a new
project. You will need to choose a name for the project (let's say
"myproject"), and for the main script ("runme")::

    $ git clone git://github.com/sheenams/aws_scripts.git aws_scripts

execution
=========

The ``aws`` script provides the user interface, and uses standard
UNIX command line syntax. Note that for development, it is convenient
to run ``aws`` from within the project directory by specifying the
relative path to the script::

    % cd aws_scripts
    % ./aws --help

or::

   % path/to/aws_scripts/aws --help

When invoked this way, the local version of the package is imported,
even if the version of the package is installed to the system. This is
very handy for development, and can avoid the requirement for a
virtualenv in many cases.

Commands are constructed as follows. Every command starts with the
name of the script, followed by an "action" followed by a series of
required or optional "arguments". The name of the script, the action,
and options and their arguments are entered on the command line
separated by spaces. Help text is available for both the ``aws``
script and individual actions using the ``-h`` or ``--help`` options.

