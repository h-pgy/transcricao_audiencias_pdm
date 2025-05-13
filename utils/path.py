import os
from typing import Optional

def create_folder_if_not_exists(folder_path:str)->str:

    if not os.path.exists(folder_path):

        os.mkdir(folder_path)

    return os.path.abspath(folder_path)


def solve_path(path:str, parent:Optional[str]=None)->str:

    if parent:
        parent = create_folder_if_not_exists(parent)
        path = os.path.join(parent, path)
    
    return os.path.abspath(path)