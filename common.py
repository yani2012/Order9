# -*- coding: utf-8 -*-
import pickle
import pandas as pd
import sys
import threading
from datetime import timedelta
import log_helper

root_path = './'
sys.path.append(root_path)
import tushare as ts
try:
   df = ts.get_stock_basics()[['name','outstanding','totals']].reset_index().rename(columns = {'code':'ticker','name':'secShortName'}).sort_values('ticker').set_index('ticker')
   df.to_csv(root_path + '/stkNames.csv',encoding = 'GBK')
except:
   pass
stock_info_df = pd.read_csv(root_path + "/stkNames.csv", encoding = 'gbk', dtype = {'ticker':str}).set_index('ticker')

def qs2ps(qs):
    return unicode(qs.toUtf8(), 'utf-8', 'ignore')

def pickle_dump(file, data):  
    #with保证自动关闭文件  
    #设置文件模式为'wb'来以二进制写模式打开文件  
    with open(file,'wb') as f:  
        #dump()函数接受一个可序列化的Python数据结构  
        pickle.dump(data,f)  
        log_helper.info('[info]pickle_dump success')  
   
#反序列化  
def pickle_load(file):  
    with open(file,'rb') as f:  
        return(pickle.load(f))

def start_thread(name, target_function, is_background=True):
    log_helper.info('[info]start_thread:{0}'.format(name))
    work_thread = threading.Thread(target=target_function)
    work_thread.setName(name)
    work_thread.setDaemon(is_background)
    work_thread.start()

def get_stock_name(stock):
    try:
        stock_name = stock_info_df.ix[stock]['secShortName']
    except:
        stock_name = '******'

    return stock_name

def get_total_shares(stock):
    try:
        total_shares = stock_info_df.ix[stock]['totals']
    except:
        total_shares = 0.0

    return total_shares

def get_order_key(user_name, order_id):
     return '{0}_{1}'.format(user_name, order_id)

def get_order_vol(capital, position_percent, price):
    if price == 0:
        log_helper.error('price is 0 when get order vol')
        return 0
    ret = int(capital * position_percent / (price * 100)) * 100
    #log_helper.info('get order vol {3}[{0}, pos_cent:{1}, price:{2}]'.format(capital, position_percent, price, ret))
    return ret

def percent2float(position_percent_str):
    #the input is 'x%'
    ret = float(position_percent_str[:-1])/100
    return ret

def get_reverse_repo(position_df):
    if position_df is None:
        return 0.0
    reverse_repo = 0.0
    len_position_df = len(position_df)
    if len_position_df > 0:
        for i in range(len_position_df):
            rowData = position_df.iloc[i]
            if rowData['CostValue'] == 0.0 and rowData['MarketValue'] > 0:
                reverse_repo = rowData['MarketValue']
                log_helper.info('get reverse_repo:{0}'.format(reverse_repo))
                continue
    return reverse_repo

def get_reverse_repo2(position_df, position_value = 0.0):
    if position_df is None:
        return position_value - 0.0
    reverse_repo = 0.0
    len_position_df = len(position_df)
    total_market_value = 0
    if len_position_df > 0:
        for i in range(len_position_df):
            rowData = position_df.iloc[i]
            if rowData['CostValue'] != 0.0 and rowData['MarketValue'] > 0:
                total_market_value += rowData['MarketValue']

    return position_value - total_market_value if position_value > total_market_value else 0.0

def get_pos_percent(position_value, total_asset, reverse_repo):
    stock_value = position_value - reverse_repo
    pos_percent = 0.0
    if total_asset>0:
        pos_percent = round(stock_value/total_asset,2)

    return pos_percent

def get_total_max_position_percent(position_percent_str):
    #the input is 'x%'
    ret = float(position_percent_str[:-1])/100
    if ret > 1:
        ret = 1
    return ret

def check_position_limit(account_cache, userName, to_buy_percent=0.0, max_limit=0.5):
    if userName not in account_cache.keys():
        return False
    if 'pos_percent' not in account_cache[userName].keys():
        return False

    current_pos_percent = account_cache[userName]['pos_percent']
    #print('current percent:{0}, to_buy_percent:{1}, max_limit:{2}'.format(current_pos_percent, to_buy_percent, max_limit))
    if (current_pos_percent + to_buy_percent) > max_limit:
        return False

    return True

def available_close_vol(account_cache, userName, stock, percent = 1):
    if userName not in account_cache.keys():
        return 0
    
    positions = account_cache[userName]['position'].set_index('StockCode')
    if stock not in positions.index:
        log_helper.error('no position on {0} when stop loss'.format(stock))
        return 0

    position_size = positions['CoverableSize'][stock]
    if position_size == 0:
        return 0

    if percent == 1:
        return position_size

    vol = int(position_size*percent/100)*100
    if vol == 0:
        return position_size

    return vol

def trading_day(current_date=pd.Timestamp('today')):
    trading_day = current_date
    if trading_day.hour >= 15:
        trading_day = trading_day + timedelta(days=1)

    if trading_day.dayofweek == 5:
        trading_day = trading_day + timedelta(days=2)
    elif trading_day.dayofweek == 6:
        trading_day = trading_day + timedelta(days=1)

    return str(trading_day.dayofyear)

def is_in_trade_time():
    now = pd.Timestamp('today')
    minutesNo = now.hour*60 + now.minute
    if minutesNo > 900 or minutesNo < 555:
        return False

    return True

def is_in_sell_time():
    now = pd.Timestamp('today')
    minutesNo = now.hour*60 + now.minute
    if minutesNo > 900 or minutesNo < 567:
        return False

    return True

def get_ask5_price(market_data):
    price = round(market_data['ask5_px'], 2)
    if price > 0:
        return price
    log_helper.warn('the price might meet UpLimit')
    price = round(market_data['ask1_px'], 2)
    if price > 0:
        return price

    return round(market_data['bid1_px'], 2)

def get_bid5_price(market_data):
    price = round(market_data['bid5_px'], 2)
    if price > 0:
        return price
    log_helper.warn('the price might meet DownLimit')
    price = round(market_data['bid1_px'], 2)
    if price > 0:
        return price

    return round(market_data['ask1_px'], 2)

def is_open_high_limit(market_data):
    pre_close = market_data['pre_close']
    high_limit = round(pre_close*1.1, 2)
    return abs(market_data['open'] - high_limit) < 0.01

# if __name__=='__main__':
#     d1 = pd.Timestamp('2018-03-09 14:30')
#     print(d1, ' ', trading_day(d1))

#     d1 = pd.Timestamp('2018-03-09 15:30')
#     print(d1, ' ', trading_day(d1))

#     d1 = pd.Timestamp('2018-03-10 14:30')
#     print(d1, ' ', trading_day(d1))

#     d1 = pd.Timestamp('2018-03-11 14:30')
#     print(d1, ' ', trading_day(d1))

#     d1 = pd.Timestamp('2018-03-12 14:30')
#     print(d1, ' ', trading_day(d1))

#     d1 = pd.Timestamp('2018-03-12 16:30')
#     print(d1, ' ', trading_day(d1))

#     d1 = pd.Timestamp('2018-03-13 14:30')
#     print(d1, ' ', trading_day(d1))


    