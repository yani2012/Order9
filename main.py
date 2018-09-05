# -*- coding: utf-8 -*-
"""
# -*- coding: utf-8 -*-
Spyder Editor
This is a temporary script file.
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from copy import deepcopy
import sys
import datetime
import time
import os
from dlltrader import DllTrader, unique_columns
import pandas as pd
from time_condition_helper import TimeConditionHelper
from data_cache_manager import DataCacheManager, BasePoolItem,SellPoolItem,PriceWay
from market_data_helper import MDHelper
from common import root_path, start_thread, qs2ps, pickle_dump, pickle_load,get_stock_name,percent2float,get_total_max_position_percent,check_position_limit
import Queue
import threading
import qt_main_window
import qt_helper
import common
import log_helper
import time_condition_helper
import buy_sell_work
import itertools
from collections import OrderedDict


class TestDialog(QMainWindow, qt_main_window.MainWindow):  
    def __init__(self,parent=None):  
        log_helper.info('[info]Init forms')
        super(TestDialog,self).__init__(parent)  
        self.setupUi(self)  
        self._mdHelper = MDHelper()
        self.data_cache_manager = DataCacheManager(self._mdHelper)
        self.price_way = PriceWay()
        self.tradable = False
        self.timeConditionHelper = TimeConditionHelper()
        self.current_pnl_percent = 0.0
        self.current_cost_px = 0.0
        self.intraday_high_dict = {}
        self.init_down_limit_vols_dict = {}

        self.order_vols_queue_dict = {}
        self.is_queued_order_vol_dict = {}
        self.sellTimeFlag = False 

        self.slot_setPosLimit()  ##仓位设置
        self.position_stock_info_dict = {}
        self.is_save_position_stock_info = False

        self.pushButton_addAcc.clicked.connect(self.slot_addAccount)                         ##001界面与后台运算函数衔接  “加入账户按钮”
        self.pushButton_delAcc.clicked.connect(self.slot_delAccount)                         ##002删除账户按钮
        self.qtable_accounts.itemDoubleClicked.connect(self.slot_selAccount)                 ##003双击选中账号列表
        self.qtable_positions.itemDoubleClicked.connect(self.slot_select_position)           ##004双击持仓列表关联到卖出位置             
        self.pushButton_addSellCondition.clicked.connect(self.slot_addSellCondition)         #005卖出界面卖出条件按钮
        self.tableWidget_stopLoss.itemDoubleClicked.connect(self.slot_delSellCondition)      #006卖出界面列表双击
        self.horizontalSlider_posLimit.valueChanged.connect(self.slot_setPosLimit)           #007仓位设置（登录时）
        self.qtable_orders.itemDoubleClicked.connect(self.slot_cancelOrder)                  #008双击取消
        self.pushButton_save.clicked.connect(self.slot_save)                                 #009保存
        self.pushButton_load.clicked.connect(self.slot_load)                                 #010载入
        self.pushButton_refreshAcc.clicked.connect(self.slot_refreshAccount)                 #011刷新  
        self.pushButton_changeTimeRange.clicked.connect(self.slot_changeTimeRange)           #012改变时间范围
        self.pushButton_changeMaxTradeTimes.clicked.connect(self.slot_changeMaxTradeTimes)   #013改变最大成交次数
        self.pushButton_importStocks.clicked.connect(self.slot_importstocks)                 #014导入股票
        self.pushButton_clearAll.clicked.connect(self.slot_clearPool)                        #015清除所有
        self.pushButton_commitVPBuy.clicked.connect(self.slot_addVPBuyCondition)                       #016--确认按钮---
        self.tableWidget_VPBuy.itemDoubleClicked.connect(self.slot_delVPBuyCondition)                  #017 一板池双击删除
        self.pushButton_commitUpLimitBuy.clicked.connect(self.slot_addUpLimitBuyCondition)             #018---涨停二池确认按钮-------------
        self.tableWidget_UpLimitBuy.itemDoubleClicked.connect(self.slot_delUpLimitBuyCondition)        #019 涨停池双击删除
        self.pushButton_commitNewBuy.clicked.connect(self.slot_addNewBuyCondition)                     #020-----------------次新池确认按钮-----------
        self.tableWidget_NewBuy.itemDoubleClicked.connect(self.slot_delNewBuyCondition)                #021 次新池双击删除
        
        self.lineEdit_maxTradeCount.setText(str(qt_helper.max_trade_count_dict[qt_helper.table_name_up_limit_pool]))
        self.tabWidget_conditions.currentChanged.connect(self.slot_on_buy_condition_page_changed)     #选项页切换时调用

#------------------------------------------------------------------------------------------------------
        QtCore.QMetaObject.connectSlotsByName(self)                     #连接程序
        log_helper.info('[info]start threads')
        start_thread('auto_start_up', self.auto_start_up)               #----------M1------
        self.tradable = True
        log_helper.info('[info]tradable set tradable with true')
        self.has_query_account = {}
        self.subscribed_stocks = []
        self.market_depths_df = None
        self.monitor_stocks_depth_df = None
        self.monitor_newstocks_depth_df = None
        self.monitor_stocks = []
        self.monitor_stocks_new = []
        self.last_query_trading_time = pd.Timestamp.now()

    def auto_start_up(self):                                                  #===------------------------------启动时扫描========
        start_thread('auto_refresh', self.auto_refresh)
        start_thread('scan_upLimitBuy', self.scan_upLimitBuy)
        start_thread('scan_condition_sells', self.scan_condition_sells)

    def auto_refresh(self):                                                   #====------------------------------自动刷新=========
        while True:
            time.sleep(5)
            trading_day = common.trading_day()
            if trading_day != self.data_cache_manager.trading_day:   #auto reset cache
                self.data_cache_manager.reset()
            now = time.strftime("%H:%M:%S", time.localtime())
            if now < '09:05:00':
                continue
            if now > '23:00:00':
                break 
            try:
                self.pushButton_refreshAcc.click()
            except Exception, e:
                log_helper.error(u"[error]auto_refresh账户刷新错误:{0}".format(e))

    def scan_upLimitBuy(self):                                                #==---------------------涨停买入扫描=========
        '''
        差1分涨停买入
        '''
        while True:
            time.sleep(0.4)
            try:
                if not common.is_in_trade_time():
                    continue

                if self.market_depths_df is None:
                    time.sleep(1)
                    continue

                #涨停池扫描
                if self.timeConditionHelper.check_time(qt_helper.table_name_up_limit_pool):
                    try:                
                        buy_sell_work.buy_up_limit_work(self, self.data_cache_manager, self.data_cache_manager.UpLimitBuyConditions
                        , qt_helper.table_name_up_limit_pool)
                    except Exception,e:
                        log_helper.error(u'[error]请检查涨停池买入条件单是否正确:{0}'.format(e))
                else:
                    self.data_cache_manager.cancel_orders_by_pool(qt_helper.table_name_up_limit_pool)

                #一板池
                if self.timeConditionHelper.check_time(qt_helper.table_name_1stUp_limit_pool):
                    try:                
                        buy_sell_work.buy_up_limit_work(self, self.data_cache_manager, self.data_cache_manager.UpLimitBuyConditions_1st
                        , qt_helper.table_name_1stUp_limit_pool)
                    except Exception,e:
                        log_helper.error(u'[error]请检查一板池买入条件单是否正确:{0}'.format(e))
                else:
                    self.data_cache_manager.cancel_orders_by_pool(qt_helper.table_name_1stUp_limit_pool)

                #次新一板池
                if self.timeConditionHelper.check_time(qt_helper.table_name_1stnew_up_limit_pool):
                    try:                
                        buy_sell_work.buy_up_limit_work(self, self.data_cache_manager, self.data_cache_manager.UpLimitBuyConditions_1stNew
                        , qt_helper.table_name_1stnew_up_limit_pool)
                    except Exception,e:
                        log_helper.error(u'[error]请检查次新一板池买入条件单是否正确:{0}'.format(e))
                else:
                    self.data_cache_manager.cancel_orders_by_pool(qt_helper.table_name_1stnew_up_limit_pool)
            except Exception, e:
                log_helper.error('[error]scan_upLimitBuy exception:{0}'.format(e))

    def scan_condition_sells(self):                                                     #-----------卖出扫描----------------------========
        while True:
            time.sleep(0.5)
            try:
                if not self.tradable:
                    continue
                #if not common.is_in_sell_time():
                    #continue
                if self.market_depths_df is None:
                    continue

                #self.check_max_drawdown_sell()
                self.check_stoploss_sell()
            except Exception, e:
                log_helper.error('[error]scan_condition_sells exception:{0}'.format(e))


#-----------------------------------------------------------------------------------------------------------------------------
    def slot_addAccount(self):                                                                     #-----001加入账户函数--------
        '''
        将账号添加到账号列表，必须保证账号可以登陆（用户名密码正确并且dll可以登陆）
        '''
        log_helper.info('[info]slot_add_account')
        broker = qs2ps(self.comboBox_broker.currentText())     #证券公司
        userName = qs2ps(self.lineEdit_userName.text())        #用户名
        trdPwd = qs2ps(self.lineEdit_trdPwd.text())            #用户密码
        comPwd = qs2ps(self.lineEdit_comPwd.text())            #通讯密码
        posLimit = qs2ps(self.lineEdit_posLimit.text())        #仓位限制
        
        if self.data_cache_manager.has_user(userName):         #如果数据文件里面有账户名字则提示：账户已经存在
            log_helper.warn('[warn]account exists')
            self.label_result.setText(u'账户已经存在')
            return   
        try:
            dll = DllTrader(broker, userName, trdPwd, comPwd, '')
            if dll.client is None:
                log_helper.info('add account:{0} failed'.format(userName))
                return

            balance = dll.balance()
            position_value = balance['PositionValue']
            total_asset = balance['TotalAsset']
            account_info =  {'tradeApi':dll,
                                'holder':dll.holder,
                                'broker':broker,                                                    
                                'userName':userName,
                                'moneyAccount':'',
                                'trdPwd':trdPwd,
                                'comPwd':comPwd,
                                'posLimit':posLimit,
                                'asset':total_asset,
                                'usable':balance['UsableMoney']+0.01,
                                'position_value': balance['PositionValue'],
                                'entrustAll':None,
                                'entrust':None,
                                'position':None}
            log_helper.info('------------balance_info:{0}'.format(balance))
            self.query_trading_info(account_info)
            account_info['pos_percent'] = common.get_pos_percent(position_value, total_asset, common.get_reverse_repo2(account_info['position'], position_value))
            self.data_cache_manager.update_by_user(userName, account_info)
        except Exception,e:
            self.data_cache_manager.delete_user(userName)
            log_helper.error(u'[error]账户登陆错误:{0}'.format(e))
        self.slot_writeAccounts()

    def slot_delAccount(self):                                                    #--------002删除账号函数-----------
        '''
        从账号列表中删除账号）
        '''    
        curAcc = qs2ps(self.lineEdit_curAcc.text())
        self.data_cache_manager.delete_user(curAcc)
        
        self.lineEdit_curAcc.setText('')
        #self.lineEdit_curPosLimit.setText('')
        self.lineEdit_curAsset.setText('')
        self.lineEdit_curUsable.setText('')

        self.slot_writeAccounts()
        self.tableWidget_stopLoss.clearContents()
        self.qtable_orders.clearContents()
        self.qtable_positions.clearContents()


    def slot_selAccount(self):                                                     #----------------------003选中账户函数
        '''
        从账号列表中选中账号
        '''
        row = self.qtable_accounts.currentRow()
        userName = qs2ps(self.qtable_accounts.item(row, 2).text())
        self.UpdateControlsByAccount(userName)
   
    def slot_select_position(self):                                                #----------------------004 双击关联
        row = self.qtable_positions.currentRow()
        stock_code = qs2ps(self.qtable_positions.item(row, 0).text())
        self.lineEdit_stkAutoSell.setText(stock_code)
        self.lineEdit_stkSell.setText(stock_code)
        self.lineEdit_stkNeutralSell.setText(stock_code)
        self.lineEdit_order_intrument.setText(stock_code)
        self.lineEdit_stock_MaxDrawdownSell.setText(stock_code)
        self.current_pnl_percent = float(self.qtable_positions.item(row, 8).text()[:-1])*0.01
        stock_hold_qty = float(self.qtable_positions.item(row, 2).text())
        self.current_cost_px = 0.0 if stock_hold_qty ==0.0 else float(self.qtable_positions.item(row, 5).text())/stock_hold_qty
        available_sell_vol = qs2ps(self.qtable_positions.item(row, 3).text())

    def slot_setPosLimit(self):                                                   #----------------------007 仓位限制条指向
        qt_helper.update_position_limit(self.horizontalSlider_posLimit,self.lineEdit_posLimit)

    def slot_cancelOrder(self):                                                   #======================008双击===========
        curAcc = qs2ps(self.lineEdit_curAcc.text())
        row = self.qtable_orders.currentRow()
        stock_code = qs2ps(self.qtable_orders.item(row, 1).text())
        entruID = qs2ps(self.qtable_orders.item(row, 7).text())
        log_helper.info('cancel orders for[{0}, stock_code:{1}, order_id:{2}]'.format(curAcc, stock_code, entruID))
        self.data_cache_manager.accounts[curAcc]['tradeApi'].cancel_withID(stock_code, entruID)
        time.sleep(0.5)
        self.data_cache_manager.accounts[curAcc]['entrust'] = self.data_cache_manager.accounts[curAcc]['tradeApi'].query_active_orders()
        self.slot_writeEntrust()


    def slot_save(self):                                                          #-------------------009 保存按钮
        accounts = self.data_cache_manager.accounts
        dll_backup = {}
        for username in list(accounts.keys()):
            dll_backup.update({username:accounts[username]['tradeApi']})

        for username in list(accounts.keys()):
            accounts[username]['tradeApi'] = None

        trading_day = common.trading_day()
        if trading_day != self.data_cache_manager.trading_day:
            self.data_cache_manager.reset()
        pickle_dump(root_path + '/config.pkl', {'account_cache':self.data_cache_manager.accounts,
        trading_day:{#'jxcBuyConditions':self.data_cache_manager.jxcBuyConditions,
                    'stop_loss_dict':self.data_cache_manager.stop_loss_dict,
                    'max_drawdown_dict':self.data_cache_manager.max_drawdown_dict,
                    #'stop_profit_dict':self.data_cache_manager.stop_profit_dict,
                    #'neutral_sell_dict':self.data_cache_manager.neutral_sell_dict,
                    #'pBuyConditions':self.data_cache_manager.pBuyConditions,
                    'vpBuyConditions':self.data_cache_manager.UpLimitBuyConditions_1st,
                    'UpLimitBuyConditions_1stNew':self.data_cache_manager.UpLimitBuyConditions_1stNew,
                    #'dxcBuyConditions':self.data_cache_manager.dxcBuyConditions,
                    #'zxcBuyConditions':self.data_cache_manager.zxcBuyConditions,
                    'UpLimitBuyConditions':self.data_cache_manager.UpLimitBuyConditions,
                    'orderkeyset:': self.data_cache_manager.orderkeyset,
                    'pool2tradecount:': self.data_cache_manager.pool2tradecount,
                    'orderid2pooldict:': self.data_cache_manager.orderid2pooldict,
                    'run_time_dict':time_condition_helper.run_time_dict,
                    'max_trade_dict':qt_helper.max_trade_count_dict,
                    }})

        for username in list(accounts.keys()):
            accounts[username]['tradeApi'] = dll_backup[username]
        
    def slot_load(self):                                                        ## -------------------------010载入按钮
        config = pickle_load(root_path + '/config.pkl')
        trading_day = common.trading_day()
        self.data_cache_manager = DataCacheManager(self._mdHelper)
        if 'account_cache' in config:
            self.data_cache_manager.accounts = config['account_cache']
        if trading_day in config.keys():
            trading_cache = config[trading_day]
            self.data_cache_manager.stop_loss_dict = trading_cache['stop_loss_dict']
            self.data_cache_manager.max_drawdown_dict = trading_cache['max_drawdown_dict']
            if 'vpBuyConditions' in trading_cache.keys():
                self.data_cache_manager.UpLimitBuyConditions_1st = trading_cache['vpBuyConditions']
            if 'UpLimitBuyConditions_1stNew' in trading_cache.keys():
                self.data_cache_manager.UpLimitBuyConditions_1stNew = trading_cache['UpLimitBuyConditions_1stNew']
            if 'UpLimitBuyConditions' in trading_cache.keys():
                self.data_cache_manager.UpLimitBuyConditions = trading_cache['UpLimitBuyConditions']
            if 'orderkeyset' in trading_cache.keys():
                self.data_cache_manager.orderkeyset = trading_cache['orderkeyset']
            if 'pool2tradecount' in trading_cache.keys():
                self.data_cache_manager.pool2tradecount = trading_cache['pool2tradecount']
            if 'orderid2pooldict' in trading_cache.keys():
                self.data_cache_manager.orderid2pooldict = trading_cache['orderid2pooldict']
            if 'pool2ordersdict' in trading_cache.keys():
                self.data_cache_manager.pool2ordersdict = trading_cache['pool2ordersdict']

            if 'run_time_dict' in trading_cache.keys():
                time_condition_helper.run_time_dict = trading_cache['run_time_dict']

            if 'max_trade_dict' in trading_cache.keys():
                qt_helper.max_trade_count_dict = trading_cache['max_trade_dict']

            self._add_stockcode_list_by_dict(self.data_cache_manager.stop_loss_dict)
            #self._add_stockcode_list_by_dict(self.data_cache_manager.pBuyConditions)
            #self._add_stockcode_list_by_dict(self.data_cache_manager.vpBuyConditions)
            self._add_stockcode_list_by_dict(self.data_cache_manager.UpLimitBuyConditions)

        user_names = list(self.data_cache_manager.accounts)
        info = ""
        for username in user_names:
            account = self.data_cache_manager.accounts[username]
            try:
                self.data_cache_manager.accounts[username]['tradeApi'] = DllTrader(account['broker'],
                                                account['userName'],
                                                account['trdPwd'],
                                                account['comPwd'],
                                                account['moneyAccount'])
            except Exception,e:
                log_helper.error('[error]!!!!!!exception happend when load user({0}). exception:{1}'.format(username, e))
                info += u'加载{0}失败. '.format(username)
            
            self.data_cache_manager.check_user_when_load(username)

        if len(info) == 0:
            info = u'加载成功'
        self.label_result.setText(info)
        self.slot_refreshAccount()   # 刷新账户

        position_stock_info_file = root_path + '/big_up_avg_close.pkl'
        if os.path.exists(position_stock_info_file):
            log_helper.info('load {0}'.format(position_stock_info_file))
            self.position_stock_info_dict = pickle_load(position_stock_info_file)
            log_helper.info('get position_stock_info_dict{0}'.format(self.position_stock_info_dict))

    def slot_refreshAccount(self):                                                         #--------------------011刷新账户
        self.timeConditionHelper.set_tradable(self.tradable)
        user_names = list(self.data_cache_manager.accounts)
        now = pd.Timestamp.now()
        time_diff = (now-self.last_query_trading_time).total_seconds()
        for userName in user_names:
            try:
                account = self.data_cache_manager.accounts[userName]
                balance = account['tradeApi'].balance()
                account['asset'] = balance['TotalAsset']
                account['position_value'] = balance['PositionValue']
                #log_helper.info('----------balance:{0}'.format(balance))
                #log_helper.info('----------account usable:{0}'.format(account['usable']))
                if 'usable' in account and account['usable']==balance['UsableMoney'] and userName in self.has_query_account.keys():
                    #the UsableMoney not changed, no need to query other info
                    continue

                account['usable'] = balance['UsableMoney']
                position_value = balance['PositionValue']
                total_asset = balance['TotalAsset']
                self.has_query_account[userName] = 1
                self.last_query_trading_time = now
                self.query_trading_info(account)
                account['pos_percent'] = common.get_pos_percent(position_value, total_asset, common.get_reverse_repo2(account['position'], position_value))
                
            except Exception, e:
                log_helper.error(u'[error]slot_refreshAccount账户刷新错误:{0} for account:{1}'.format(e, userName))
                try:
                    account['tradeApi'].refresh()
                except Exception, e:
                    log_helper.error(u'[error]relogin failed with exception:{0} for account:{1}'.format(e, userName))

        self.slot_writeAccounts()
        userName = qs2ps(self.lineEdit_curAcc.text())
        self.UpdateControlsByAccount(userName)

    def slot_changeTimeRange(self):                                                         #-------------012改变时间范围
        current_page_index = self.tabWidget_conditions.currentIndex()
        pool_name = buy_sell_work.get_pool_name(current_page_index)
        log_helper.info('change page:{0} time range[{1}, {2}]'.format(current_page_index, self.qt_begin_time.time(), self.qt_end_time.time()))
        time_condition_helper.run_time_dict[pool_name] = [(self.qt_begin_time.time(), self.qt_end_time.time())]

    def slot_changeMaxTradeTimes(self):                                                     #-------------013改变成交次数
        current_page_index = self.tabWidget_conditions.currentIndex()
        max_count = int(self.lineEdit_maxTradeCount.text())
        log_helper.info('change page:{0} max_trade_times[{1}]'.format(current_page_index, max_count))
        pool_name = buy_sell_work.get_pool_name(current_page_index)
        qt_helper.max_trade_count_dict[pool_name] = max_count


    def slot_importstocks(self):                                                            #------------014导入股票按钮
        current_page_index = self.tabWidget_conditions.currentIndex()
        stocks = self._read_stocks()

        if current_page_index == 0:#vol_px
            for stock in stocks:
                self.lineEdit_stkVPBuy.setText(stock)
                self.slot_addVPBuyCondition()

        elif current_page_index == 1:#up_limit
            for stock in stocks:
                self.lineEdit_stkUpLimitBuy.setText(stock)
                self.slot_addUpLimitBuyCondition()

        elif current_page_index == 2:#new
            for stock in stocks:
                self.lineEdit_stkNewBuy.setText(stock)
                self.slot_addNewBuyCondition()

    def slot_clearPool(self):                                             #------015清除所有   (通过股票池索引对当前选中的股票出做全部清除）
        current_page_index = self.tabWidget_conditions.currentIndex()

        if current_page_index == 0:          #vol_px
            #self.data_cache_manager.clear_dict_values(self.data_cache_manager.vpBuyConditions)
            self.data_cache_manager.clear_dict_values(self.data_cache_manager.UpLimitBuyConditions_1st)
            self.tableWidget_VPBuy.clearContents()
        elif current_page_index == 1:          #up_limit
            self.data_cache_manager.clear_dict_values(self.data_cache_manager.UpLimitBuyConditions)
            self.tableWidget_UpLimitBuy.clearContents()
        elif current_page_index == 2:
            self.data_cache_manager.clear_dict_values(self.data_cache_manager.UpLimitBuyConditions_1stNew)
            self.tableWidget_NewBuy.clearContents()

#------------------------------------------------------------------------------------------必须的支持函数------------
    def _read_stocks(self):                                              #-导入股票时读取TXT文本股票
        stocks = []
        stock_name_file = QFileDialog.getOpenFileName(self,  
                                    "选取文件",  
                                    os.getcwd(),  
                                    "Text Files (*.txt);;All Files (*)")   #设置文件扩展名过滤,注意用双分号间隔  
        if not os.path.exists(stock_name_file):
            log_helper.error("[error] stock name file({0}) doesn't exists.".format(stock_name_file))
            return stocks

        
        file = open(stock_name_file, 'r')
        line_arr = file.readlines()
        line_arr = [item.strip() for item in line_arr]
        for item in line_arr:
            if len(item) != 6:
                continue
            stocks.append(item)

        return stocks

    def slot_writeAccounts(self):     #----------账户登录，刷新等时候产生作用
        '''
        将账户信息刷新到表中
        '''
        self.qtable_accounts.clearContents()
        i = 0
        user_names = list(self.data_cache_manager.accounts)
        for username in user_names:
            acc = self.data_cache_manager.accounts[username]
            self.qtable_accounts.setItem(i, 0, QtGui.QTableWidgetItem(acc['holder']))
            self.qtable_accounts.setItem(i, 1, QtGui.QTableWidgetItem(acc['broker']))
            self.qtable_accounts.setItem(i, 2, QtGui.QTableWidgetItem(acc['userName']))
            self.qtable_accounts.setItem(i, 3, QtGui.QTableWidgetItem(acc['posLimit']))
            self.qtable_accounts.setItem(i, 4, QtGui.QTableWidgetItem(str(acc['asset'])))
            self.qtable_accounts.setItem(i, 5, QtGui.QTableWidgetItem(str(acc['usable'])))
            if 'pos_percent' in acc.keys():
                self.qtable_accounts.setItem(i, 6, QtGui.QTableWidgetItem('{0}%'.format(100 * acc['pos_percent'])))
            i += 1

    def UpdateControlsByAccount(self, userName):          #——————————————  刷新账户设置信息
        if len(userName) > 0:
            acc = self.data_cache_manager.accounts[userName]
            self.lineEdit_curAcc.setText(acc['userName'])
            self.lineEdit_curAsset.setText(str(acc['asset']))
            self.lineEdit_curUsable.setText(str(acc['usable']))
            #self.horizontalSlider_curPosLimit.setValue(int(acc['posLimit'][:-1])/10)

            self.slot_writeSellConditions()
            self.slot_writeNewBuyConditions()
            #self.slot_writeVPBuyConditions()
            self.slot_writeUpLimitBuyConditions()
            self.slot_writeEntrust()
            #self.slot_writePosition()

    def _add_stockcode_list_by_dict(self, cache):
        for user_name in cache.keys():
            for stock_code in cache[user_name]:
                self._add_stockcode_list(stock_code)

    def _add_stockcode_list(self, stock_code):
        if stock_code not in self.subscribed_stocks:
            log_helper.info('add stock code:{0} to subscribed_stocks'.format(stock_code))
            self.subscribed_stocks.append(stock_code)

    def query_trading_info(self, account_info):    #----------------------------------------交易信息，很多地方用到
        log_helper.info('query_trading_info:{0} begin'.format(account_info['userName']))
        trade_df = account_info['entrustAll'] = account_info['tradeApi'].query_all_orders()[['StockCode','EntruId','EntruPrice','EntruVol','OrderState','DealVol','EntruTime']]
        account_info['position'] = account_info['tradeApi'].position()
        self.update_position_stock_info(account_info['position'])
        active_orders =  account_info['tradeApi'].query_active_orders()
        #log_helper.info('active orders:{0}'.format(active_orders))
        account_info['entrust'] = active_orders

        now = pd.Timestamp('today')
        if now.hour >= 15 or now.hour < 9:
            return
        for i in range(len(trade_df)):
            rowData = trade_df.iloc[i]
            self.data_cache_manager.update_trade_count(account_info['userName'], rowData['EntruId'], rowData['OrderState'])
        log_helper.info('query_trading_info:{0} finish'.format(account_info['userName']))

    def update_position_stock_info(self, position_df):           #登录时就会调用
        log_helper.info('update_position_stock_info begin')
        if position_df is None:
            return
        
        for i in range(len(position_df)):
            position_i = position_df.iloc[i]
            stock_code = position_i['StockCode']
            if stock_code in self.position_stock_info_dict.keys():
                continue

            position_qty = position_i['TotalSize']
            if position_qty == 0:
                continue

            position_stock_info = PositionStockInfo(stock_code)
            position_stock_info.total_shares = common.get_total_shares(position_stock_info.stock)
            self.position_stock_info_dict[stock_code] = position_stock_info
            log_helper.info('add {0}'.format(position_stock_info.log_str()))

            self._add_stockcode_list(stock_code)
        log_helper.info('update_position_stock_info finish')

    def slot_writeEntrust(self):                                        #--------双击列表时调用---------
        self.qtable_orders.clearContents()
        curAcc = qs2ps(self.lineEdit_curAcc.text())
        if curAcc not in self.data_cache_manager.accounts.keys():
            self.data_cache_manager.accounts[curAcc] = OrderedDict()
            return
        entrust = self.data_cache_manager.accounts[curAcc]['entrust']
        if entrust is not None:
            for i in range(len(entrust)):
                entrust_i = entrust.iloc[i]
                self.qtable_orders.setItem(i, 0, QtGui.QTableWidgetItem(entrust_i['EntruTime']))
                self.qtable_orders.setItem(i, 1, QtGui.QTableWidgetItem(entrust_i['StockCode']))
                self.qtable_orders.setItem(i, 2, QtGui.QTableWidgetItem(entrust_i['SotckName']))
                self.qtable_orders.setItem(i, 3, QtGui.QTableWidgetItem(u'买入' if entrust_i['Direction']==0 else u'卖出'))
                self.qtable_orders.setItem(i, 4, QtGui.QTableWidgetItem(str(entrust_i['EntruPrice'])))
                self.qtable_orders.setItem(i, 5, QtGui.QTableWidgetItem(str(entrust_i['EntruVol'])))
                self.qtable_orders.setItem(i, 6, QtGui.QTableWidgetItem(str(entrust_i['DealVol'])))
                self.qtable_orders.setItem(i, 7, QtGui.QTableWidgetItem(entrust_i['EntruId']))




    #==============================================================================#量价涨停池条件相关操作
    def slot_addVPBuyCondition(self):                                                                         #------------016 涨停按钮
        log_helper.info('slot_addVPBuyCondition')
        stock_code =  qs2ps(self.lineEdit_stkVPBuy.text())
        #如果代码为空，直接跳过
        if stock_code.strip() =="":
            return
        self._add_stockcode_list(stock_code)
        self.data_cache_manager.add_pool_item(self.lineEdit_curAcc, stock_code
            , self.comboBox_posVPBuy, self.data_cache_manager.UpLimitBuyConditions_1st, self.tableWidget_VPBuy, self.price_way.up_limit_pool_1st)

    def slot_writeVPBuyConditions(self):                                                                      #写入买入条件
        self.data_cache_manager.update_table_widget(self.tableWidget_VPBuy, self.lineEdit_curAcc
        , self.data_cache_manager.UpLimitBuyConditions_1st)

    def slot_delVPBuyCondition(self):                                                                         #--------------017---清除股票
        log_helper.info('slot_delVPBuyCondition')
        stock = self.data_cache_manager.del_pool_item(self.lineEdit_curAcc, self.data_cache_manager.UpLimitBuyConditions_1st, self.tableWidget_VPBuy)

    def slot_on_buy_condition_page_changed(self):                                                             #-----------022------------
        current_page_index = self.tabWidget_conditions.currentIndex()
        pool_name = buy_sell_work.get_pool_name(current_page_index)
        buy_sell_work.update_time_range(self, pool_name)

#==============================================================================#次新一板池条件相关操作
    def slot_addNewBuyCondition(self):                                                                         #----------020---------
        log_helper.info('slot_addNewBuyCondition')
        stock_code =  qs2ps(self.lineEdit_stkNewBuy.text())
        #如果代码为空，直接跳过
        if stock_code.strip() =="":
            return
        self._add_stockcode_list(stock_code)
        self.data_cache_manager.add_pool_item(self.lineEdit_curAcc, stock_code
            , self.comboBox_posNewBuy, self.data_cache_manager.UpLimitBuyConditions_1stNew, self.tableWidget_NewBuy, self.price_way.up_limit_pool_1st)

    def slot_writeNewBuyConditions(self):
        self.data_cache_manager.update_table_widget(self.tableWidget_NewBuy, self.lineEdit_curAcc
        , self.data_cache_manager.UpLimitBuyConditions_1stNew)

    def slot_delNewBuyCondition(self):                                                                       #-------021--------
        log_helper.info('slot_delNewBuyCondition')
        stock = self.data_cache_manager.del_pool_item(self.lineEdit_curAcc, self.data_cache_manager.UpLimitBuyConditions_1stNew, self.tableWidget_newBuy)

#==============================================================================#涨停池条件相关操作
    def slot_addUpLimitBuyCondition(self):                                                                   #------018确认按钮
        stock_code =  qs2ps(self.lineEdit_stkUpLimitBuy.text())
        #如果代码为空，直接跳过
        if stock_code.strip() =="":
            return
        self._add_stockcode_list(stock_code)
        self.data_cache_manager.add_pool_item(self.lineEdit_curAcc, stock_code
            , self.comboBox_posUpLimitBuy, self.data_cache_manager.UpLimitBuyConditions, self.tableWidget_UpLimitBuy, self.price_way.up_limit_pool)

    def slot_writeUpLimitBuyConditions(self):                                                        #----写入条件-------
        self.data_cache_manager.update_table_widget(self.tableWidget_UpLimitBuy, self.lineEdit_curAcc
        , self.data_cache_manager.UpLimitBuyConditions)

    def slot_delUpLimitBuyCondition(self):                                                           #-------019双击删除
        self.data_cache_manager.del_pool_item(self.lineEdit_curAcc, self.data_cache_manager.UpLimitBuyConditions, self.tableWidget_UpLimitBuy)  

#=================================================止损卖出条件相关操作=========================
    def slot_addSellCondition(self):                                                                 #---005卖出界面卖出条件按钮 ---BUG----
        stock_code = qs2ps(self.lineEdit_stkSell.text())   #股票代码
        #如果代码为空，直接跳过
        if stock_code.strip() =="":
            return
        self._add_stockcode_list(stock_code)
        userName = qs2ps(self.lineEdit_curAcc.text())                                                                       #账户名
        vol_sell_percent = percent2float(qs2ps(self.comboBox_volStopLoss.currentText()))                                    #卖出数量百分比
        vol = common.available_close_vol(self.data_cache_manager.accounts, userName, stock_code, percent=vol_sell_percent)  #卖出数量(通过百分比进行的换算）
        trigger_condition = qs2ps(self.combox_trigger_condition.currentText())                                              #卖出条件选择
        waySell = qs2ps(self.comboBox_waySell.currentText())                                                                #挂单方式
        poolItem = SellPoolItem(userName, stock_code, vol, waySell, trigger_condition=trigger_condition)                    #卖出列表
        
        if not self.data_cache_manager.has_sell_item(poolItem.get_key(), self.data_cache_manager.stop_loss_dict[userName]):
            log_helper.info('add stop loss item:{0} for user:{1}'.format(poolItem.log_str(), userName))
            if poolItem.stock not in self.data_cache_manager.stop_loss_dict[userName].keys():
                self.data_cache_manager.stop_loss_dict[userName][poolItem.stock] = [poolItem]
            else:
                self.data_cache_manager.stop_loss_dict[userName][poolItem.stock].append(poolItem)
            self.slot_writeSellConditions()
            
    def slot_delSellCondition(self):                                                                         # -----------------006”双击删除“函数
        self.data_cache_manager.del_pool_item(self.lineEdit_curAcc, self.data_cache_manager.stop_loss_dict
            , self.tableWidget_stopLoss, update_table_widget=self.slot_writeSellConditions)
        
    def slot_writeSellConditions(self):                                                                      #--------写入卖出条件--------
        self.tableWidget_stopLoss.clearContents()
        curAcc = qs2ps(self.lineEdit_curAcc.text())
        if len(curAcc) == 0:
            return

        if curAcc not in self.data_cache_manager.stop_loss_dict.keys():
            self.data_cache_manager.stop_loss_dict[curAcc] = OrderedDict()
            return
        poolItemDict = self.data_cache_manager.stop_loss_dict[curAcc]
        entrust = self.data_cache_manager.accounts[curAcc]['entrustAll']

        i = 0
        for poolItem in  itertools.chain.from_iterable(list(poolItemDict.values())):
            self.tableWidget_stopLoss.setItem(i, 0, QtGui.QTableWidgetItem(poolItem.stock))
            self.tableWidget_stopLoss.setItem(i, 1, QtGui.QTableWidgetItem(get_stock_name(poolItem.stock)))
            self.tableWidget_stopLoss.setItem(i, 2, QtGui.QTableWidgetItem(str(poolItem.vol)))
            self.tableWidget_stopLoss.setItem(i, 3, QtGui.QTableWidgetItem(poolItem.trigger_condition))
            self.tableWidget_stopLoss.setItem(i, 4, QtGui.QTableWidgetItem(poolItem.waySell))

            #把所有委托编号对应的成交信息返回到界面 
            if entrust is not None:
                if poolItem.state!=None and poolItem.state in entrust['EntruId'].values:
                    info = entrust[entrust['EntruId'] == poolItem.state]
                    self.tableWidget_stopLoss.setItem(i, 5, QtGui.QTableWidgetItem(str(info['EntruVol'].iloc[0])))
                    self.tableWidget_stopLoss.setItem(i, 6, QtGui.QTableWidgetItem(str(info['EntruPrice'].iloc[0])))
                    self.tableWidget_stopLoss.setItem(i, 7, QtGui.QTableWidgetItem(str(info['DealVol'].iloc[0])))
                    self.tableWidget_stopLoss.setItem(i, 8, QtGui.QTableWidgetItem(info['OrderState'].iloc[0]))
            i += 1

# =================================================卖出===========================================================================================
    def check_stoploss_sell(self):
        try:
            is_after_9_40 = self.chb_stoploss_time.isChecked()
            if is_after_9_40:
                now = pd.Timestamp('today')
                minutesNo = now.hour * 60 + now.minute
                if minutesNo > 580:
                    return

            buy_sell_work.sell_work(self, self.data_cache_manager, self.data_cache_manager.stop_loss_dict
                                    , qt_helper.table_name_stop_loss, buy_sell_work.stop_loss_check)
        except Exception, e:
            log_helper.error(u'[error]请检查止损卖出条件单是否正确:{0}'.format(e))

#==============================================================================================

app=QApplication(sys.argv)  
dialog=TestDialog()  
dialog.show() 
#dialog.load_data_background()
app.exec_()  