import os

from utils import OUTPUTS_FOLDER

def reset_app():
    # Delete the outputs folder
    os.system(f"rm -rf {OUTPUTS_FOLDER}")

    # Recreate the outputs folder
    os.mkdir(OUTPUTS_FOLDER)
