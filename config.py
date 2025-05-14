import os
from typing import Optional, Union, Type
from dotenv import load_dotenv

from utils.path import create_folder_if_not_exists, solve_path


def load_env_var(varname:str, cast_type:Optional[Type]=None)->Union[int, float, bool, str]:
    """
    Loads the value of an environment variable from a .env file.
    This function uses the `load_dotenv` method to load environment variables
    from a .env file into the environment, and then retrieves the value of the
    specified variable.
    Args:
        varname (str): The name of the environment variable to retrieve.
    Returns:
        str: The value of the specified environment variable.
    Raises:
        KeyError: If the specified environment variable is not found.
    """

    # Carrega variáveis de ambiente do .env
    load_dotenv()

    try:
        value = os.environ[varname]
    except KeyError:
        raise RuntimeError(f'Environment variable {varname} not defined.')
    
    if cast_type is not None:
        try:
            value = cast_type(value)
        except ValueError:
            raise ValueError(f'Cannot cast environment variable {varname} to {cast_type.__name__}.')
    return value

AZURE_SPEECH_KEY: str = load_env_var("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION: str = load_env_var("AZURE_SPEECH_REGION")


DATA_FOLDER: str = create_folder_if_not_exists(load_env_var('DATA_FOLDER'))

WAV_FOLDER: str = solve_path('youtube_wav_files', DATA_FOLDER)

SAS_TTL_SECONDS: int = load_env_var("SAS_TTL_SECONDS", int)

AZURE_STORAGE_CONNECTION_STRING: str = load_env_var("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME: str = load_env_var("AZURE_STORAGE_CONTAINER_NAME")