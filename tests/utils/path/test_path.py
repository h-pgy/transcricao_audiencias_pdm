import os
import pytest
from utils.path import create_folder_if_not_exists, solve_path
import shutil

@pytest.fixture
def temp_folder(tmp_path):
    try:
        yield str(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            # Clean up the temporary directory after the test
            # This is important to avoid leaving temporary files behind
            # and to ensure that each test runs in a clean environment.
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

def test_solve_path_with_absolute_path(temp_folder):
    absolute_path = os.path.join(temp_folder, "absolute_folder")
    result = solve_path(absolute_path)
    assert result == os.path.abspath(absolute_path), 'Expected absolute path to match'

def test_solve_path_with_relative_path_and_parent(temp_folder):
    parent_folder = os.path.join(temp_folder, "parent_folder")
    relative_path = "child_folder"
    result = solve_path(relative_path, parent=parent_folder)
    expected_path = os.path.join(parent_folder, relative_path)
    assert result == os.path.abspath(expected_path)

def test_solve_path_with_relative_path_without_parent(temp_folder):
    relative_path = "orphan_folder"
    result = solve_path(relative_path)
    assert result == os.path.abspath(relative_path)

def test_solve_path_creates_parent_folder(temp_folder):
    parent_folder = os.path.join(temp_folder, "new_parent")
    relative_path = "child_folder"
    result = solve_path(relative_path, parent=parent_folder)
    assert os.path.exists(parent_folder)
    assert os.path.isdir(parent_folder)
    assert result == os.path.abspath(result)