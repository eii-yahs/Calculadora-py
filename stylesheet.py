from pathlib import Path
import re

ROOT_DIR = Path(__file__).parent
IMAGE_DIR = ROOT_DIR / 'imagens'
ICON = IMAGE_DIR / 'logo3.png'

PRIMARY = '#5282FF'
DARKER = '#2056CB'
DARKEST = '#002E80'
PRIMARY2 = '#201F1F'
DARKER2 = '#1A191A'
DARKEST2 = '#111111'

BIG_FONT = 40
MEDIUM_FONT = 24
SMALL_FONT = 18
MARGIN = 15
MINIMUM_WIDTH = 500

DIGIT_REGEX = re.compile(r'^[0-9.]$')

def is_num_or_dot(string: str):
    return bool(DIGIT_REGEX.search(string))

def conver_num(string: str):
    number = float(string)
    if number.is_integer():
        number = int(number)
    return number

def is_valid_number(string: str):
    valid = False
    try:
        float(string)
        valid = True
    except ValueError:
        valid = False
    return valid

def is_empty(string: str):
    return len(string) == 0