import os
import pathlib
import time


MAIN_PATH = pathlib.Path(__file__).parent.parent.resolve()
LOG_PATH = os.path.join(MAIN_PATH, "logs\\", f'{time.strftime("%Y-%m-%d_%H-%M-%S")}.log')