from __future__ import absolute_import
from __future__ import unicode_literals

import contextlib
import errno
import os
import random
import string
import subprocess as subprocess_module

import pytest


@pytest.fixture(scope='session')
def subprocess():
    def subprocess_func(cmd):
        proc = subprocess_module.Popen(
            cmd,
            stdout=subprocess_module.PIPE,
            stderr=subprocess_module.PIPE,
            shell=True
        )
        out, err = proc.communicate()
        return proc.returncode, out, err
    return subprocess_func


@pytest.fixture(scope='session')
def create_test_file():
    """
    Create a working directory and some test files
    """
    def create_test_file_func(filepath, contents):
        try:
            # create subdirs as necessary
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(filepath):
                pass

        # create test file in dir
        with open(filepath, 'w') as f:
            f.write(str(contents))

        # return file creation time
        return os.stat(filepath).st_ctime
    return create_test_file_func


@pytest.fixture(scope='function')
def password():
    return ''.join(random.choice(string.lowercase) for i in xrange(10))


@pytest.fixture(scope='function')
def cd():
    @contextlib.contextmanager
    def cd_func(new_path):
        """ Context manager for changing the current working directory """
        saved_path = os.getcwd()
        try:
            os.chdir(new_path)
            yield new_path
        finally:
            os.chdir(saved_path)
    return cd_func
