# encoding: utf-8

import os

# Common folder to store logs etc.
DOTFILES = os.path.expanduser('~') + '/.config/blackcat'

# Used for logging
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
#10 = DEBUG, 50 = CRITICAL
DEBUG_LEVEL = 20
LOG_FILE = DOTFILES + '/blackcat.log'
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'

# Import handlers from these files
APPS = (
    'example',
    'unknown'
)
