import os
import pytest
import self as self
from mock import patch
from LabelManagerApp.labelimageapp import directoryop


TESTFOLDER = ['testfolder', (os.path.join('testfolderA', 'testfolderB'))]
TESTFILENAME = ['project1', 'project23']


@pytest.mark.parametrize("projectname", TESTFILENAME)
@pytest.mark.parametrize("filepath", TESTFOLDER)
@pytest.mark.parametrize("filepathdest", TESTFOLDER)
@patch('os.mkdir')
@patch('os.chdir')
@patch('os.getcwd')
@patch('shutil.move')
def test_createsubdirectories(mock_mkdir, mock_chdir, mock_getcwd, self, projectname, filepath):
    save = create_subdirectories(self, projectname)
    assert mock_mkdir.call_count == 4
    assert mock_chdir.call_count == 2
    assert mock_getcwd.call_count == 1
    assert save == projectname


def test_rename_move_file(mock_shutil_move, filepath, filepathdest, projectname):
    dirname = rename_move_file(self, filepath, filepathdest, projectname)
    assert mock_shutil_move == 1
    assert projectname == dirname
