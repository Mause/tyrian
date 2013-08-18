.. tyrian documentation master file, created by
   sphinx-quickstart on Sun Aug 18 12:19:24 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to tyrian's documentation!
==================================

Tyrian is a simplistic `LISP`_ implementation, with only the most basic of features implemented.
The standard library functions are to be written in python for simplicitys sake, see :doc:`user_docs/standard_library`

.. _LISP: http://en.wikipedia.org/wiki/Common_Lisp

Basic usage is as follows;


.. code-block:: sh

    $ python cli.py <options> <input_filename> <output_filename>


Contents:

.. toctree::
   :maxdepth: 2

   theory/index.rst

   user_docs/index.rst

   dev_docs/index.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
