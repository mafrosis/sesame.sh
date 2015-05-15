from __future__ import absolute_import
from __future__ import unicode_literals

import os


def test_encrypt_file_already_exists(tmpdir, subprocess, cd, create_test_file, password):
    """
    Single file test, using relative paths
    Ensure encrypt is aborted when file exists
    """
    # create a single test file
    test_file_path = 'file.test'
    fake_output_file = 'fake'

    with cd(tmpdir.strpath):
        create_test_file(test_file_path, '')

        # create a fake output file that sesame.sh should not overwrite
        create_test_file(fake_output_file, '')

        # grab the inode number of the test file; use this to check file has
        # been overwritten
        inode_num = os.stat(fake_output_file).st_ino

        # encrypt the test file
        ret, stdout, stderr = subprocess(
            'sesame.sh e -p {} {} {}'.format(password, fake_output_file, test_file_path)
        )
        # sesame.sh will abort a call to bash's read after 5 secs
        # a timeout on read causes retcode 4
        assert ret == 4

        # ensure file not overwritten, and message is displayed
        assert inode_num == os.stat(fake_output_file).st_ino
        assert 'File exists at' in stderr
        assert 'Aborted on timeout' in stdout


def test_decrypt_file_already_exists(tmpdir, subprocess, cd, create_test_file, password):
    """
    Single file test, using relative paths
    Ensure the error occurs and decrypt is aborted when file exists
    """
    # create a single test file
    test_file_path = 'file.test'

    with cd(tmpdir.strpath):
        create_test_file(test_file_path, '')

        # encrypt the test file - passing relative path
        ret, stdout, stderr = subprocess(
            'sesame.sh e -p {} {}'.format(password, test_file_path)
        )
        assert ret == 0

        # ensure output file has been created
        assert os.path.exists('{}.sesame'.format(test_file_path))

        # grab the inode number of the current file; use this to check file has
        # been overwritten
        inode_num = os.stat(test_file_path).st_ino

        # decrypt the test file
        ret, stdout, stderr = subprocess(
            'sesame.sh d -p {} {}.sesame'.format(password, test_file_path)
        )
        # sesame.sh will abort a call to bash's read after 5 secs
        # a timeout on read causes retcode 4
        assert ret == 4

        # ensure file not overwritten, and message is displayed
        assert inode_num == os.stat(test_file_path).st_ino
        assert 'File exists at' in stderr
        assert 'Aborted on timeout' in stdout
