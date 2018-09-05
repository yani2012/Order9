# -*- coding: utf-8 -*-
import logging  
import logging.handlers  
import pandas as pd

today = pd.Timestamp('today')
file_name = 'app_{0}_{1}_{2}'.format(today.year, today.month, today.day)
LOG_FILE = '{0}.log'.format(file_name)
  
file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 10*1024*1024, backupCount=5)  
fmt = '%(asctime)s -%(name)s - %(levelname)s - %(message)s'  
formatter = logging.Formatter(fmt)  
file_handler.setFormatter(formatter)  

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
  
logger = logging.getLogger('app')  
logger.addHandler(file_handler)
#logger.addHandler(console_handler)
logger.setLevel(logging.INFO)  
  
def info(information):
    try:
        logger.info(information)
    except:
        pass

def error(information):
    try:
        logger.error(information)
    except:
        pass

def warn(information):
    try:
        logger.warn(information)
    except:
        pass
 