# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from dlltrader import DllTrader
from PyQt4 import QtCore, QtGui

from collections import OrderedDict

from market_data_helper import MDHelper
from common import qs2ps, get_stock_name
import common
import qt_helper
import log_helper
import itertools
import math

class PriceWay(object):
    def __init__(self):    
        #self.px_pool = u'1.07倍'
        #self.avg_px_pool = u'卖5价'
        #self.low_px_pool = u'卖5价'
        #self.vol_px_pool = u'涨停价'
        self.up_limit_pool = u'涨停价'
        self.up_limit_pool_1st = u'涨停价'
        #self.selected_pool = u'卖5价'
        self.stop_loss_pool = u'买5价'
        self.stop_profit_pool = u'买5价'

class BasePoolItem(object):
    def __init__(self, stock, pos, price_way):
        self.stock = stock
        self.pos = pos
        #self.high = high
        self.price_way = price_way
        self.state = None
        self.is_sent_order = False
        
    def log_str(self):
        return u'poolItem[{0}, pos:{1}, price_way:{2}, state:{3}, is_sent_order:{4}]'.format(
            self.stock, self.pos, self.price_way, self.state, self.is_sent_order)
    def __repr__(self):
        return self.log_str()

class SellPoolItem(object):
    def __init__(self, user_name, stock, vol, waySell, trigger_condition=None, price=None):
        self.user_name = user_name
        self.stock = stock
        self.vol = vol
        self.waySell = waySell
        self.price = price
        self.trigger_condition = trigger_condition
        self.state = None
        self.is_sent_order = False

    def get_key(self):
        return '{0}_{1}_{2}'.format(self.user_name, self.stock, self.trigger_condition)

    def log_str(self):
        return 'SellPoolItem[{0}][{1}, vol:{2}, waySell:{3}, price:{4}, trigger_condition:{5}, state:{6}, is_sent_order:{7}]'.format(
            self.user_name, self.stock, self.vol, self.waySell, self.price, self.trigger_condition, self.state, self.is_sent_order)

class PositionStockInfo(object):
    def __init__(self, stock_code):
        self.stock = stock_code
        self.total_shares = 0.0 #单位亿
        self.total_market_value = 0.0 #总市值

    def log_str(self):
        return 'PositionStockInfo[{0}, total_shares:{1}, total_market_value:{2}, big_up_avg_close:{3}]'.format(
            self.stock, self.total_shares, self.total_market_value, self.big_up_avg_close)

    def __str__(self):
        return self.log_str()

class DataCacheManager(object):
    def __init__(self, mdHelper):
        self._mdHelper = mdHelper
        self.trading_day = common.trading_day()
        self.accounts = OrderedDict()
        self.stop_loss_dict = OrderedDict()
        self.max_drawdown_dict = OrderedDict()
        self.UpLimitBuyConditions = OrderedDict()
        self.UpLimitBuyConditions_1st = OrderedDict()
        self.UpLimitBuyConditions_1stNew = OrderedDict()
        self.orderid2pooldict = {}
        self.pool2ordersdict = {}
        self.pool2tradecount = {}
        self.orderkeyset = set()

    def reset(self):
        self.trading_day = common.trading_day()
        self.clear_dict_values(self.stop_loss_dict)
        self.clear_dict_values(self.max_drawdown_dict)
        self.clear_dict_values(self.UpLimitBuyConditions)
        self.clear_dict_values(self.self.UpLimitBuyConditions_1st)
        self.clear_dict_values(self.self.UpLimitBuyConditions_1stNew)
        self.clear_dict_values(self.pool2tradecount)
        self.orderid2pooldict = {}
        self.pool2ordersdict = {}
        self.orderkeyset = set()

    def add_orderid_to_dict(self, pool_name, stock_code, order_id, account_id):
        if pool_name not in self.pool2ordersdict.keys():
            self.pool2ordersdict[pool_name] = {}
        self.pool2ordersdict[pool_name][order_id] = (account_id, stock_code)

    def get_pool_trade_count(self, user_name, pool_name):
        pool_key = '{0}_{1}'.format(user_name, pool_name)
        return self.pool2tradecount.get(pool_key, 0)
    
    def cancel_orders_by_pool(self, pool_name, user_name=None):
        if pool_name not in self.pool2ordersdict.keys():
            return
        
        for key in self.pool2ordersdict[pool_name].keys():
            account_id = self.pool2ordersdict[pool_name][key][0]
            if user_name is not None and user_name!=account_id:
                continue

            stock_code = self.pool2ordersdict[pool_name][key][1]
            self.accounts[account_id]['tradeApi'].cancel_withID(stock_code, key)

        self.pool2ordersdict[pool_name] = {}

    def exceed_max_trade_count(self, user_name, pool_name):
        trade_count = self.get_pool_trade_count(user_name, pool_name)
        max_count = qt_helper.max_trade_count_dict[pool_name]
        ret = (trade_count >= max_count)

        if ret:
            self.cancel_orders_by_pool(pool_name, user_name=user_name)

        return ret


    def update_trade_count(self, user_name, order_id, order_state):
        log_helper.info('username:{0}, order_id:{1}, orderstate:{2}'.format(user_name, order_id, order_state))
        if order_state != u'已成':
            return

        order_key = common.get_order_key(user_name, order_id)
        if order_key in self.orderkeyset:
            log_helper.info('{0} has already counted'.format(order_key))
            return
        
        if order_key not in self.orderid2pooldict.keys():
            log_helper.info('order key[{0} not in orderid2pooldict]'.format(order_key))
            return
        pool_name = self.orderid2pooldict[order_key]
        poolkey = '{0}_{1}'.format(user_name, pool_name)
        if pool_name in self.pool2ordersdict.keys():
            if order_id in self.pool2ordersdict[pool_name].keys():
                self.pool2ordersdict[pool_name].pop(order_id)
    
        if poolkey not in self.pool2tradecount.keys():
            self.pool2tradecount[poolkey] = 1
        else:
            self.pool2tradecount[poolkey] += 1

        self.orderkeyset.add(order_key)
        log_helper.info('order_key:{0}, poolkey:{1}, tradecount:{2}'.format(order_key, poolkey, self.pool2tradecount[poolkey]))

    def has_user(self, userName):
        return userName in self.accounts.keys()
    
    def has_sell_item(self, key, pool_item_dict):   #将卖出条件加入列表
        ret = False
        for item in itertools.chain.from_iterable(list (pool_item_dict.values())):
            #log_helper.info('itemkey:{0},new_key:{1} compare'.format(item.get_key(), key))
            if key == item.get_key():
                log_helper.info('itemkey:{0},new_key:{1} equal'.format(item.get_key(), key))
                ret = True
                break
        return ret

    def delete_user(self, userName):
        log_helper.info('delete user:{0}'.format(userName))
        if userName in self.accounts:
            self.accounts.pop(userName)
        if userName in self.stop_loss_dict:
            self.stop_loss_dict.pop(userName)
        if userName in self.max_drawdown_dict:
            self.max_drawdown_dict.pop(userName)
        if userName in self.UpLimitBuyConditions:
            self.UpLimitBuyConditions.pop(userName)
        if userName in self.UpLimitBuyConditions_1st:
            self.UpLimitBuyConditions_1st.pop(userName)

        if userName in self.UpLimitBuyConditions_1stNew:
            self.UpLimitBuyConditions_1stNew.pop(userName)            

    def update_by_user(self, userName, account_info):
        self.accounts.update({userName:account_info})

        self.UpLimitBuyConditions.update({userName:OrderedDict()})
        self.UpLimitBuyConditions_1st.update({userName:OrderedDict()})
        self.UpLimitBuyConditions_1stNew.update({userName:OrderedDict()})

        self.stop_loss_dict.update({userName:OrderedDict()})
        self.max_drawdown_dict.update({userName:OrderedDict()})
        self.pool2tradecount.update({userName:{}})

    def check_user_when_load(self, userName):
        log_helper.info('check_user_when_load for userName:{0}'.format(userName))
        if userName not in self.UpLimitBuyConditions.keys():
            self.UpLimitBuyConditions.update({userName:OrderedDict()})
        if userName not in self.UpLimitBuyConditions_1st.keys():
            self.UpLimitBuyConditions_1st.update({userName:OrderedDict()})
        if userName not in self.UpLimitBuyConditions_1stNew.keys():
            self.UpLimitBuyConditions_1stNew.update({userName:OrderedDict()})
        if userName not in self.stop_loss_dict.keys():
            self.stop_loss_dict.update({userName:OrderedDict()})
        if userName not in self.max_drawdown_dict.keys():
            self.max_drawdown_dict.update({userName:OrderedDict()})
        if userName not in self.pool2tradecount.keys():
            self.pool2tradecount.update({userName:{}})

    def add_pool_item(self, line_edit_account, stock, combo_pos, dict_cache, targetTableWidget, price_way, apply_all = False):
        userName = qs2ps(line_edit_account.text())
        if len(userName) > 0:
            pos = qs2ps(combo_pos.currentText())        

            if apply_all:
                for userName in dict_cache.keys():
                    poolItem = BasePoolItem(stock, pos, price_way)
                    if poolItem.stock not in dict_cache[userName].keys():
                        dict_cache[userName][poolItem.stock] = poolItem
                        log_helper.info('[info] [apply all] add {0} for user:{1}'.format(poolItem.log_str(), userName))
            else:
                poolItem = BasePoolItem(stock, pos, price_way)
                if poolItem.stock not in dict_cache[userName].keys():
                    dict_cache[userName][poolItem.stock] = poolItem
                    log_helper.info('[info]add {0} for user:{1}'.format(poolItem.log_str(), userName))

            self.update_table_widget(targetTableWidget, line_edit_account, dict_cache)
        else:
            log_helper.warn(u"[warn]请先选中账户")
        return None

    def del_pool_item(self, line_edit_account, dict_cache, targetTableWidget, update_table_widget=None):
        accounts = list(dict_cache.keys())
        stock = ''
        for account in accounts:
            stock = str(targetTableWidget.item(targetTableWidget.currentRow(),0).text())
            if stock in dict_cache[account].keys():
                del dict_cache[account][stock]
        if update_table_widget is None:
            self.update_table_widget(targetTableWidget, line_edit_account, dict_cache)
        else:
            update_table_widget()

        return stock

    def update_table_widget(self, targetTableWidget, line_edit_account, dict_cache):
        curAcc = qs2ps(line_edit_account.text())
        if len(curAcc) == 0:
            log_helper.warn(u"[warn]请先选中账户")
            return

        targetTableWidget.clearContents()
        if curAcc not in dict_cache.keys():
            log_helper.warn('[warn] {0} not in cache'.format(curAcc))
            dict_cache[curAcc] = OrderedDict()
            return

        current_account_cache = dict_cache[curAcc]
        entrust = self.accounts[curAcc]['entrustAll']
        i = 0
        for item in current_account_cache.values():
            k = 0
            targetTableWidget.setItem(i, k, QtGui.QTableWidgetItem(item.stock))
            k += 1
            targetTableWidget.setItem(i, k, QtGui.QTableWidgetItem(get_stock_name(item.stock)))
            k += 1
            targetTableWidget.setItem(i, k, QtGui.QTableWidgetItem(item.pos))
            table_name = str(qs2ps(targetTableWidget.objectName()))
            #print('targetTableWidget.objectName:', table_name)
            
            # 把所有委托编号对应的成交信息返回到界面
            state = item.state
            #print('account:', curAcc, ' table:', targetTableWidget.objectName, ' state:', state)
            if state is None:
                i += 1
                continue

            targetTableWidget.setItem(i, k, QtGui.QTableWidgetItem(state))
            if state in entrust['EntruId'].values:
                info = entrust[entrust['EntruId'] == state]
                #log_helper.info('info:{0}, state:{1}, {2}'.format(info, state, info['OrderState'].iloc[0]))
                targetTableWidget.setItem(i, k, QtGui.QTableWidgetItem(info['OrderState'].iloc[0]))

            i += 1

    def get_stock_list(self, dict_cache):
        stock_list = []
        for tempUser in dict_cache:
            subDict = dict_cache[tempUser]
            for key in subDict.keys():  # 所有价格池
                if key not in stock_list:
                    stock_list.append(key)

        return stock_list

    def clear_dict_values(self, dict_cache):
        for key in dict_cache.keys():
            dict_cache[key] = {}


# if __name__ == '__main__':
#     import pandas as pd
#     data = pd.read_pickle('D:\\work\\projects\\config.pkl')
#     print(data['80'].pBuyConditions)

   