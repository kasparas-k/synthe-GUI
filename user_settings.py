'''
    user_settings.py

    User settings and variables, dependent on the user's configuration are here.
'''

WIN_W = 400
WIN_H = 300

'''
    Default plot setup values.
'''
XCENTER = 429.75
XDELTA = 0.15
YTOP = 1.02
YDELTA = 0.2

SYN_LS = '-'
SYN_MARKER = ''

'''
    PATHS TO VARIOUS THINGS
'''
CACHE_LAST = True
SAVE_SYNTHETIC_SPECTRA = True
OUTPUT_LOG_DIR = './'

SHORTEN_LIST = False # save a separate version of the list with all the saved fits excluded
INPUT_LIST_PATH = './input_list.txt'
SHORT_LIST_PATH = './input_list.short'

kurucz_bin_dir = '/mnt/win/astrosp2/lnx/kurucz/bin/'
atomic_line_dir = '/mnt/win/astrosp2/lnx/kurucz/lines/'
molecular_line_dir = '/mnt/win/astrosp2/lnx/kurucz/lines/'
synthe_sh_path = ''

MOD_DIR = r'/mnt/win/astrosp2/hd122563_uves_blue/'
SPEC_DIR = r'/mnt/win/astrosp2/hd122563_uves_blue/'


'''
    SYNTHE
'''
DEFAULT_PARAMS = {
    'vrot':'0.53',
    'vmac':'3.90',
    'resolution':'60000.',
    'abn':'5.24',
}

PARAM_BOUNDARIES = {
    'vrot':2,
    'vmac':2,
    'abn':0.5
}

ELEMENT = '6'
VTURB = '1.500E+05'

# ABUNDANCE_SCALE = 0.7 # RGB Stars in 47 Tuc
ABUNDANCE_SCALE = 0.7 

FIT_DELAY = 0.1
