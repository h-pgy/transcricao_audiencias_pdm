import os
from dotenv import load_dotenv


def load_env_var(varname:str)->str:
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
        return os.environ[varname]
    except KeyError:
        raise RuntimeError(f'Environment variable {varname} not defined.')


AZURE_SPEECH_KEY = load_env_var("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = load_env_var("AZURE_SPEECH_REGION")
