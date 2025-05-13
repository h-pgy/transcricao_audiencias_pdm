import os
import pytest
from utils.path import create_folder_if_not_exists
import shutil

@pytest.fixture
def temp_folder(tmp_path):
    try:
        yield str(tmp_path)
    finally:
        shutil.rmtree(tmp_path)

def test_create_folder_if_not_exists_creates_folder(temp_folder):
    folder_path = os.path.join(temp_folder, "new_folder")
    result = create_folder_if_not_exists(folder_path)
    assert os.path.exists(folder_path)
    assert os.path.isdir(folder_path)
    assert result == os.path.abspath(folder_path)

def test_create_folder_if_not_exists_returns_existing_folder(temp_folder):
    folder_path = os.path.join(temp_folder, "existing_folder")
    os.mkdir(folder_path)
    result = create_folder_if_not_exists(folder_path)
    assert os.path.exists(folder_path)
    assert os.path.isdir(folder_path)
    assert result == os.path.abspath(folder_path)

def test_create_folder_if_not_exists_handles_nested_folders(temp_folder):
    nested_folder_path = os.path.join(temp_folder, "nested", "folder")
    with pytest.raises(FileNotFoundError):
        create_folder_if_not_exists(nested_folder_path)