from __future__ import absolute_import
from __future__ import unicode_literals

import os
import shutil
import uuid


def test_single_file_relative_paths(tmpdir, subprocess, cd, create_test_file, password):
    """
    Single file test, using relative paths
    Encrypted filename should default to inputfile + '.sesame'
    """
    # create a single test file
    test_file_path = 'file.test'
    test_file_contents = str(uuid.uuid4())

    with cd(tmpdir.strpath):
        create_test_file(test_file_path, test_file_contents)

        # encrypt the test file - passing relative path
        ret, stdout, stderr = subprocess(
            'sesame.sh e -p {} {}'.format(password, test_file_path)
        )

        # ensure output file has been created
        assert os.path.exists('{}.sesame'.format(test_file_path))

        # delete input file (to test decrypt)
        os.remove(test_file_path)

        # decrypt the test file
        ret, stdout, stderr = subprocess(
            'sesame.sh d -p {} {}.sesame'.format(password, test_file_path)
        )

        # ensure decrypted file has been created
        assert os.path.exists(test_file_path)

        # verify decrypted contents
        with open(test_file_path, 'r') as f:
            assert test_file_contents == f.read()


def test_single_file_absolute_paths(tmpdir, subprocess, cd, create_test_file, password):
    """
    Single file test, using absolute paths
    Encrypted filename should default to inputfile + '.sesame'
    """
    # create a single test file
    test_file_path = 'file.test'
    test_file_contents = str(uuid.uuid4())

    with cd(tmpdir.strpath):
        create_test_file(test_file_path, test_file_contents)

        # encrypt the test file - passing absolute path
        ret, stdout, stderr = subprocess(
            'sesame.sh e -p {} {}'.format(password, test_file_path)
        )

        # ensure output file has been created
        assert os.path.exists('{}.sesame'.format(test_file_path))

        # delete input file (to test decrypt)
        os.remove(test_file_path)

        # decrypt the test file
        ret, stdout, stderr = subprocess(
            'sesame.sh d -p {} {}.sesame'.format(
                password, os.path.join(tmpdir.strpath, test_file_path)
            )
        )

        # verify decrypted contents at the absolute extracted path
        with open(test_file_path, 'r') as f:
            assert test_file_contents == f.read()


def test_multiple_files(tmpdir, subprocess, cd, create_test_file, password):
    """
    Multiple files test, using relative paths
    Encrypted filename should default to inputfile + '.sesame'
    """
    # setup a dict with mutiple test files
    test_file_paths = {
        '1.test': str(uuid.uuid4()),
        '2.test': str(uuid.uuid4()),
    }
    output_filename = 'test.sesame'

    with cd(tmpdir.strpath):
        # create files
        for path, content in test_file_paths.iteritems():
            create_test_file(path, content)

        # encrypt the test files
        ret, stdout, stderr = subprocess(
            'sesame.sh e -p {} {} {}'.format(
                password, output_filename, ' '.join(test_file_paths.keys())
            )
        )

        # ensure output file has been created
        assert os.path.exists(output_filename)

        # delete input files (to test decrypt)
        for path in test_file_paths.keys():
            os.remove(path)

        # decrypt the test file
        ret, stdout, stderr = subprocess(
            'sesame.sh d -p {} {}'.format(password, output_filename)
        )

        # ensure decrypted files have been created
        for path in test_file_paths.keys():
            assert os.path.exists(path)

        # verify decrypted contents
        for path, content in test_file_paths.iteritems():
            with open(path, 'r') as f:
                assert content == f.read()


def test_directory(tmpdir, subprocess, cd, create_test_file, password):
    """
    Single directory test, with one file & relative paths
    Encrypted filename should default to inputdir + '.sesame'
    """
    test_dir_path = 'test_dir'
    test_file_path = os.path.join(test_dir_path, 'file.test')
    test_file_contents = str(uuid.uuid4())

    with cd(tmpdir.strpath):
        # create a directory and a single test file
        create_test_file(test_file_path, test_file_contents)

        # encrypt the test directory - passing relative path
        ret, stdout, stderr = subprocess(
            'sesame.sh e -p {} {}'.format(password, test_dir_path)
        )

        # ensure output file has been created
        assert os.path.exists('{}.sesame'.format(test_dir_path))

        # delete input dir (to test decrypt)
        shutil.rmtree(test_dir_path)

        # decrypt the test file
        ret, stdout, stderr = subprocess(
            'sesame.sh d -p {} {}.sesame'.format(password, test_dir_path)
        )

        # ensure decrypted dir and file have been created
        assert os.path.exists(test_dir_path)
        assert os.path.exists(test_file_path)

        # verify decrypted file contents
        with open(test_file_path, 'r') as f:
            assert test_file_contents == f.read()
