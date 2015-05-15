Sesame.sh
=========

A pure bash implementation of Sesame encrypt/decrypt tool, [originally developed](https://pypi.python.org/pypi/sesame) in Python.

Sesame provides a tar-like interface to encrypt & decrypt one or more files and directories, primarily to enable sensitive configuration files to be included in source control.

Sesame was inspired by a [blog post](http://ejohn.org/blog/keeping-passwords-in-source-control) by [@jeresig](https://twitter.com/jeresig).


Tests
-----

The test framework for `sesame.sh` is written in Python using [`pytest`](http://pytest.org/latest).

Use the following to install `pytest` and run the tests (assumes working Python install):

    sudo pip install pytest
    py.test

A couple of the tests run for 5 seconds (waiting for a timeout from bash's `read`), you can run all but the slow tests with:

    py.test -m 'not slow'
