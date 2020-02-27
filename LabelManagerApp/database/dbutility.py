# file: dbutility.py
# author: Muhammad Mushfiqur Rahman <mushfiq.rahman@tum.de>
# date: 05-21-2019
'''
# This file implements database related other functional task-> 
    - date conversion.
    - all kinds of string operation etc.
'''


import datetime
import pytz
import tzlocal

from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

def time_iso8601():
    # time according to iso 8601 including local time zone
    timestamp = datetime.datetime.now()
    tz_local = tzlocal.get_localzone()
    timestamptz = tz_local.localize(timestamp)
    return timestamptz

def dict_to_cs_str(modelObj,order):
    cs_list = []
    try:
        for item in order:
            cs_list.append(f'{order[item]}: {getattr(modelObj, order[item])}')
        cs_str = ', '.join(cs_list)
    except:
        logger.error(f'Class: {type(modelObj).__name__} does not fit parameters for logging.', exc_info=True)
    return cs_str