# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import ctypes 
import pandas as pd
import TradeX
import log_helper
from broker_setting import (
    broker_setting, 
    BROKER_DLL_TYPE, 
    BROKER_ID, 
    BROKER_IP, 
    BROKER_PORT, 
    BROKER_VERSION,
    BROKER_QSID,
    BROKER_ACCOUNT_TYPE,) 
import ctypes 
dir_dll = './{0}'

def unique_columns(columns):
    return list(set(columns))

class DllTrader():
    def __init__(self, broker, username, trdPwd, txPwd, moneyID):
        '''
        dll交易接口类
        '''
        self.dll_type = broker_setting[broker][BROKER_DLL_TYPE]
        if 'tradex' in self.dll_type and username == '20305008':
            self.dll = TradeX
            self.is_tradex = True
            self.qid = broker_setting[broker][BROKER_QSID]
            self.account_type = broker_setting[broker][BROKER_ACCOUNT_TYPE]
        else:
            self.dll = ctypes.WinDLL(dir_dll.format(self.dll_type))
            self.is_tradex = False
            self.qid = None
            self.account_type = None            
                
        self.ip = broker_setting[broker][BROKER_IP]
        self.port = broker_setting[broker][BROKER_PORT]
        self.tdx_version = broker_setting[broker][BROKER_VERSION]
        self.brokerId = broker_setting[broker][BROKER_ID]   #营业部代码，请到网址 http://www.chaoguwaigua.com/downloads/qszl.htm 查询</param>  
        
        self.username = str(username)
        self.trdPwd = str(trdPwd)
        self.txPwd = str(txPwd)
        self.client = None
        self.broker = broker
        self.riskLimit = 10000000
        log_helper.info('[info]broker:{0}, serverIP:{1}, port:{2}'.format(self.broker, self.ip, self.port))
        self.query_count = 0
        
        self._openTdx()
        self._logOn()
        self.stockholder_code_sh, self.stockholder_code_sz, self.holder = self.init_stockholder_code()
        log_helper.info('init stockholder[code_sh:{0}, code_sz:{1}, holder_name:{2}]'.format(self.stockholder_code_sh, self.stockholder_code_sz, self.holder))

    def init_stockholder_code(self):
        gdInf = [i.split() for i in self._queryData(5).splitlines()]
        minLen = min([len(s) for s in gdInf])
        gdInf = [i[:minLen] for i in gdInf]
        
        try:
            stockholder_code_sh, stockholder_code_sz = [str(i) for i in pd.DataFrame(gdInf[1:], columns = gdInf[0])[u'股东代码']][:2]
            if stockholder_code_sz[0] == 'A':
                stockholder_code_sh, stockholder_code_sz = stockholder_code_sz, stockholder_code_sh
        except Exception,e:
            log_helper.error('[error]DllTrader init exception:{0}'.format(e))
            stockholder_code_sh, stockholder_code_sz = [str(i) for i in pd.DataFrame(gdInf[1:], columns = gdInf[0])[u'股东号']][:2]

        stock_holder_name = pd.DataFrame(gdInf[1:], columns = gdInf[0])[u'股东名称'].iloc[0]
        return stockholder_code_sh, stockholder_code_sz, stock_holder_name
    #==============================================================================
    #登陆、注销
    #==============================================================================
    def _openTdx(self):
        log_helper.info('[info]open tdx')
        if self.is_tradex:
            TradeX.OpenTdx(14, "6.40", 12, 0)
        else:
            self.dll.OpenTdx()
        
    def _closeTdx(self):
        log_helper.info('[info]close tdx')
        if self.is_tradex:
            return TradeX.CloseTdx()
        else:
            return self.dll.CloseTdx()
        
    def _logOn(self):
        log_helper.info('[info]user %s log on'%self.username)
        errInf = '\0' * 256
        if self.is_tradex:
            try:
                log_helper.info('tradex logon[qid:{0},ip:{1},port:{2},version:{3},brokerID:{4},accType:{5},accountID:{6}]'.format(
                    self.qid, self.ip, self.port, self.tdx_version, self.brokerId
                    , self.account_type, self.username))
                self.client = TradeX.Logon(self.qid, self.ip, self.port, self.tdx_version, self.brokerId
                    , self.account_type, self.username, self.username, self.trdPwd, self.txPwd)
            except TradeX.error, e:
                log_helper.info('logon failed. errpr:{0}'.format(e.message)) 
                TradeX.CloseTdx()
        else:
                self.client = self.dll.Logon(self.ip, self.port, self.tdx_version,
                                    self.brokerId, self.username, self.username, self.trdPwd, self.txPwd, errInf)            
                log_helper.info(errInf.decode("gbk"))    
        log_helper.info('logon got client:{0}'.format(self.client))
        
    def _logOff(self):
        #登出帐号
        if self.is_tradex:
            TradeX.Logoff(self.client)
        else:
            self.dll.Logoff(self.client)
        log_helper.info('[info]user %s log off'%self.username)
    def clear(self):
        '''
        注销账号
        关闭通达信
        '''
        self._logOff()
        self._closeTdx()
    def refresh(self):
        '''
        注销账号
        关闭通达信
        开启通达信
        登陆账号
        '''
        #self.clear()
        self._logOff()
        #self._openTdx()
        self._logOn()
    #==============================================================================
    #发单
    #==============================================================================
    def _sendOrder(self, stk, price, vol, category, priceType = 0): 
        '''
        Category 表示委托的种类
            0买入 
            1卖出  
            2融资买入  
            3融券卖出   
            4买券还券   
            5卖券还款  
            6现券还券
        PriceType 表示报价方式 
            0上海限价委托 深圳限价委托 
            1(市价委托)深圳对方最优价格  
            2(市价委托)深圳本方最优价格  
            3(市价委托)深圳即时成交剩余撤销  
            4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 
            5(市价委托)深圳全额成交或撤销 
            6(市价委托)上海五档即成转限价
        '''
        result = '\0'*256
        errInf = '\0'*256
        gddm = self.stockholder_code_sh if stk[0] == '6' else self.stockholder_code_sz
        if self.is_tradex:
            errInf, result = self.client.SendOrder(category, priceType, gddm, stk, price, vol)
            log_helper.info('tradex errInf after send order:{0}'.format(errInf))
        else:
            price = ctypes.c_float(price)
            self.dll.SendOrder(self.client, category, priceType, gddm, stk, price, vol, result, errInf) 
            log_helper.info(errInf.decode("gbk")) 
        log_helper.info(result.decode("gbk"))  
        return result.decode("gbk")
        
    def _sendOrders(self, stks, prices, vols, categorys): 
        '''
        
        stks,prices,vols 都是list格式的
        Category
            委托种类的数组，第i个元素表示第i个委托的种类，
            0买入 1卖出  2融资买入  3融券卖出   4买券还券   5卖券还款  6现券还券
        PriceType
            表示报价方式的数组,  第i个元素表示第i个委托的报价方式, 
            0上海限价委托 深圳限价委托 
            1(市价委托)深圳对方最优价格  
            2(市价委托)深圳本方最优价格  
            3(市价委托)深圳即时成交剩余撤销  
            4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 
            5(市价委托)深圳全额成交或撤销 
            6(市价委托)上海五档即成转限价
        
        '''
        stkNo = len(stks)
        
        intArray = ctypes.c_int * stkNo
        strArray = ctypes.c_char_p * stkNo
        floatArray = ctypes.c_float * stkNo
        
        result = strArray(*(['\0'*256] * stkNo))
        errInf = strArray(*(['\0'*256] * stkNo))

        c_categorys = intArray(*categorys)  
        c_priceTypes = intArray(*([0] * stkNo))
        
        
        c_gddms = strArray(*[(self.stockholder_code_sh if i [0] == '6' else self.stockholder_code_sz) for i in stks])
        c_stks = strArray(*stks)
        c_prices = floatArray(*prices)
        c_vols = intArray(*vols)

        self.dll.SendOrders(self.client, c_categorys, c_priceTypes, c_gddms, c_stks, c_prices, c_vols, stkNo, result, errInf)   
        for i in range(stkNo):
            log_helper.info(result[i].decode("gbk"))  
            log_helper.info(errInf[i].decode("gbk"))         
            
    def buy(self, stk, price, vol):
        price = round(float(price), 2)
        if vol * price > self.riskLimit:
            log_helper.error('[error]buy[stock:{0},price:{1},vol:{2}] money out of risklimit'.format(stk, price, vol))
            return   

        log_helper.info('[info]buy[stock:{0},price:{1},vol:{2},money:{3}]'.format(stk, price, vol, vol * price))
        return self._sendOrder(str(stk), float(price), int(vol), category = 0, priceType = 0)
        
        
    def sell(self, stk, price, vol):
        price = round(float(price), 2)
        if vol * price > self.riskLimit:
            log_helper.error('[error]sell[stock:{0},price:{1},vol:{2}]money out of risklimit'.format(stk, price, vol))
            return   
            
        log_helper.info('[info]sell[stock:{0},price:{1},vol:{2},money:{3}]'.format(stk, price, vol, vol * price))
        return self._sendOrder(str(stk), float(price), int(vol), category = 1, priceType = 0)
        
        
        
    def buyBasket(self, stkPriceVol):
        '''
        一篮子股票买入
        stkPriceVol：pandas.DataFrame格式
        '''
        
        if len(stkPriceVol) == 0:
            return
            
        if self.broker == u'华泰证券':
            for i in range(len(stkPriceVol)):
                stk, price, vol = stkPriceVol.iloc[i,:]
                self.buy(stk, price, vol)
        elif self.broker == u'中信建投':
            for i in range(len(stkPriceVol)):
                stk, price, vol = stkPriceVol.iloc[i,:]
                self.buy(stk, price, vol)
        else:
            stks = stkPriceVol.iloc[:, 0].astype(str)
            prices = stkPriceVol.iloc[:, 1].astype(float).map(lambda x:round(x, 2))
            vols = stkPriceVol.iloc[:, 2].astype(int)
            categorys = [0] * len(stks)
            
            if (prices * vols).max() > self.riskLimit:
                log_helper.error('[error]buyBasket: money out of risklimit')
                return
                
            self._sendOrders(list(stks), list(prices), list(vols), categorys)
        log_helper.info('[info]buyBasket:{0}'.format(stkPriceVol))
    def sellBasket(self, stkPriceVol): 
        '''
        一篮子股票卖出
        stkPriceVol：pandas.DataFrame格式
        '''
        if len(stkPriceVol) == 0:
            return
        if self.broker == u'华泰证券':
            for i in range(len(stkPriceVol)):
                stk, price, vol = stkPriceVol.iloc[i,:]
                self.sell(stk, price, vol)
        elif self.broker == u'中信建投':
            for i in range(len(stkPriceVol)):
                stk, price, vol = stkPriceVol.iloc[i,:]
                self.sell(stk, price, vol)
        else:
            stks = stkPriceVol.iloc[:, 0].astype(str)
            prices = stkPriceVol.iloc[:, 1].astype(float).map(lambda x:round(x, 2))
            vols = stkPriceVol.iloc[:, 2].astype(int)
            categorys = [1] * len(stks)
     
            if (prices * vols).max() > self.riskLimit:
                log_helper.error('[error]sellBasket: money out of risklimit')
                return
                
            self._sendOrders(list(stks), list(prices), list(vols), list(categorys))
        log_helper.info('[info]sellBasket:{0}'.format(stkPriceVol))

    def _cancel_byID(self, exchangeID, orderID, result, errInf):
        if self.is_tradex:
            errInf, result = self.client.CancelOrder(int(exchangeID), orderID)
            log_helper.info('cancel_withID[{0},order_id:{1}] result:{2} errInf:{3}'.format(exchangeID, orderID, result.decode("gbk"), errInf))
        else:
            self.dll.CancelOrder(self.client, exchangeID, str(orderID), result, errInf)
            try:
                log_helper.info('cancel_withID[{0},order_id:{1}] result:{2} errInf:{3}'.format(exchangeID, orderID, result.decode("gbk"), errInf))
            except UnicodeDecodeError:
                log_helper.error('cancel_withID[{0},order_id:{1}] error:{2}'.format(exchangeID, orderID, errInf.decode("gbk")))
        
    def cancel_withID(self, stock_code, entruID):
        result = '\0'*256
        errInf = '\0'*256
       
        exchangeID = '1' if stock_code[0] == '6' else '0'
        self._cancel_byID(exchangeID, entruID, result, errInf)

    def cancel(self, stk, direction = 'buy', method = 'all'):
        log_helper.info('cancel[stock:{0},direction:{1}]'.format(stk, direction))
        result = '\0'*256
        errInf = '\0'*256
        dir_id = 0 if direction == 'buy' else 1
        exchangeID = '1' if stk[0] == '6' else '0'
        entru = self.query_active_orders()  
        if entru is None:
            return   
        hth = entru.loc[(entru['StockCode'] == stk)&(entru['Direction'] == dir_id), ['EntruId', 'EntruTime']]   #合同编号
        hth.sort_values('EntruTime', inplace = True)

        if len(hth) == 0:
            log_helper.error('[error]请检查挂单是否存在')
            return 

        if method == 'all':
            for entruId in hth['EntruId']:
                log_helper.info(entruId)
                self._cancel_byID(exchangeID, entruID, result, errInf)      
        elif method == 'first':
            entruId = str(hth['EntruId'].iloc[0])
            self._cancel_byID(exchangeID, entruID, result, errInf)              
        elif method == 'last':
            entruId = str(hth['EntruId'].iloc[-1])
            self._cancel_byID(exchangeID, entruID, result, errInf)             
         
    def cancelAll(self, stks, direction = 'buy'):
        log_helper.info('cancelAll[stocks:{0},direction:{1}]'.format(stks, direction))
        entr = self.query_active_orders()
        if entr is None:
            return

        dir_id = 0 if direction == 'buy' else 1
        order_cancel = entr[(entr['StockCode'].isin(stks)) & (entr['Direction'] == dir_id)]
        order_cancel['ExchangeID'] = order_cancel['StockCode'].map(lambda x:'1' if x[0] == '6' else '0' )
        no_cancel = len(order_cancel)
        if no_cancel > 0:
            if self.broker in [u'华泰证券']:
                for stk in stks:
                    self.cancel(stk, direction, 'all')
            else:
                strArray = ctypes.c_char_p * no_cancel                
                result = strArray(*(['\0'*256] * no_cancel))
                errInf = strArray(*(['\0'*256] * no_cancel))
                      
                exchangeIDArr = strArray(*list(order_cancel['ExchangeID']))
                orderIDArr = strArray(*list(order_cancel['EntruId']))
                if self.is_tradex:
                    exchangeIDOrderIDTuples = tuple([(int(exchangeIDArr[i]), int(orderIDArr[i])) for i in range(len(exchangeIDArr))])
                    result = self.client.CancelOrders(exchangeIDOrderIDTuples)
                    log_helper.info('cancel orders result:{0}'.format(result))
                else:
                    self.dll.CancelOrders(self.client, exchangeIDArr, orderIDArr, no_cancel, result, errInf)
                    for i in range(no_cancel):
                        log_helper.info(result[i].decode("gbk"))  
                        log_helper.info(errInf[i].decode("gbk"))
         

    #==============================================================================
    #查询账户       
    #==============================================================================
    def _queryData(self, category = 0):
        '''
        查询各类交易数据
       Category：表示查询信息的种类，
           0资金  
           1股份   
           2当日委托  
           3当日成交     
           4可撤单   
           5股东代码  
           6融资余额   
           7融券余额  
           8可融证券   
        '''
        self.query_count += 1
        log_helper.info('query data type:{0} for account:{1}'.format(category, self.username))
        result = '\0'*1024*1024
        errInf = '\0'*256
        if self.is_tradex:
            errInf, result = self.client.QueryData(category)
        else:
            self.dll.QueryData(self.client, category, result, errInf)
        #log_helper.info('errorInt:{0}, result:{1}'.format(errInf, result.rstrip('\0')))
        result = result.rstrip('\0')
#        print(errInf.decode("gbk")) 
        result_gbk = result.decode("gbk")
        return(result_gbk)

    def balance(self):
        """
        资金余额      25164.28
        可用资金      52608.30
        冻结资金          0.00
        可取资金      25164.28
        总资产       79324.30
        最新市值      26716.00
        """
        res = self._queryData(0).splitlines()
        res = [i.split('\t') for i in res]
        length = min([len(x) for x in res])
        asset = pd.Series(res[1][:length], index=res[0][:length])      
        if self.broker == u'华福证券':
            asset = {'TotalAsset':float(asset[u'总资产'].iloc[0]),
                     'UsableMoney':float(asset[u'可用资金']),
                     'PositionValue':float(asset[u'最新市值'])} 
        else:
            asset = {'TotalAsset':float(asset[u'总资产']),
                     'UsableMoney':float(asset[u'可用资金']),
                     'PositionValue':float(asset[u'最新市值'])}         

        return asset

    def _get_dataFrame(self, result):
        result = result.splitlines()
        result = [i.split('\t') for i in result]
        len_result = len(result)
        #print('len_result:{0} result:{1}'.format(len_result, result))
        if len_result > 1:
            return pd.DataFrame(result[1:], columns=result[0])
        elif len_result == 1:
            return pd.DataFrame([], columns=result[0])
        else:
            return None

    def tdTrade(self, direction = 'buy'):
        '''
        查询当日成交
        '''
        trds = self._get_dataFrame(self._queryData(3))
        
        srcCols = [u'证券代码',u'买卖标志',u'成交价格',u'成交数量',u'成交金额']
        objCols = ['StockCode','Direction','TradePrice','TradeVolume','TradeMoney']
        
        #不同券商字段名调整
        if self.broker in [u'国联证券',u'长城证券',u'东莞证券', u'西部证券',u'华泰证券', u'东北证券', u'华福证券', u'国泰君安', u'西南证券', u'同信证券', u'兴业证券']:
            trds = trds[srcCols]
            trds.columns = [u'证券代码',u'买卖标志', u'委托类别',u'成交价格',u'成交数量',u'成交金额']
        if self.broker in [u'海通证券']:
            trds = trds[[u'证券代码',u'买卖标志', u'成交价格',u'成交数量',u'成交金额']]
            trds.columns = [u'证券代码', u'委托类别', u'买卖标志',u'成交价格',u'成交数量',u'成交金额']           
        if self.broker in [u'东海证券']:
            trds.rename(columns = {u'发生金额':u'成交金额'}, inplace = True)
        trds.rename(columns = dict(zip(srcCols, objCols)), inplace = True)
        
        #数据格式变更
        for f in ['TradePrice','TradeMoney']:
            trds[f] = trds[f].astype(float)
        for f in ['Direction','TradeVolume']:
            trds[f] = trds[f].astype(float).astype(int)
        dir_id = 0 if direction == 'buy' else 1
        trds = trds.loc[trds['Direction'] == dir_id, objCols]
        return trds
        
    def query_active_orders(self, direction = 'all'):
        '''
        可撤委托
        ['StockCode', 'SotckName','Direction','EntruPrice','EntruVol','OrderState','DealVol','EntruId','EntruTime']
        '''
        ret = self.query_orders(4, direction)
        #log_helper.info('query active orders finish:{0}'.format(ret))
        return ret

    def query_all_orders(self, direction = 'all'):
        ret = self.query_orders(2, direction)
        log_helper.info('query query_all_orders orders finish:{0}'.format(ret))
        return ret

    def query_orders(self, category, direction = 'all'):
        log_helper.info('query_orders begin')
        orders_df = self._get_dataFrame(self._queryData(category))
        #log_helper.info('orders_df:{0}'.format(orders_df))

        srcCols = [u'证券代码',u'证券名称',u'买卖标志',u'委托价格',u'委托数量',u'状态说明',u'成交数量',u'委托编号',u'委托时间']
        objCols = ['StockCode', 'SotckName','Direction','EntruPrice','EntruVol','OrderState', 'DealVol','EntruId','EntruTime']
        if orders_df is None:
            orders_df = pd.DataFrame([], columns=objCols)
            orders_df['Direction'] = orders_df['Direction'].astype(float).astype(int)
            orders_df['EntruVol'] = orders_df['EntruVol'].astype(float).astype(int)
            orders_df['DealVol'] = orders_df['DealVol'].astype(float).astype(int)
            orders_df['EntruPrice'] = orders_df['EntruPrice'].astype(float)
            return orders_df
        
        #不同券商字段名调整
        if self.broker in [u'国联证券',u'长城证券',u'东莞证券', u'华泰证券', u'西部证券', u'东北证券', u'华福证券', u'国泰君安', u'西南证券', u'同信证券', u'兴业证券']:
            orders_df = orders_df[srcCols]
            orders_df.columns = [u'证券代码',u'证券名称',u'买卖标志',u'委托类别',u'委托价格',u'委托数量',u'状态说明',u'成交数量',u'委托编号',u'委托时间']   
        elif self.broker in [u'海通证券']:
            orders_df = orders_df[srcCols]
            orders_df.columns = [u'证券代码',u'证券名称',u'委托类别',u'买卖标志',u'委托价格',u'委托数量',u'状态说明',u'成交数量',u'委托编号',u'委托时间']   
        elif self.broker == u'东海证券':
            pass
        elif self.broker == u'中信建投':
            orders_df = orders_df[srcCols]
            orders_df.columns = [u'证券代码',u'证券名称',u'买卖标志',u'委托类别', u'委托价格',u'委托数量',u'状态说明',u'成交数量',u'委托编号',u'委托时间']   
        
        orders_df = orders_df[srcCols].rename(columns = dict(zip(srcCols, objCols)))
        orders_df['Direction'] = orders_df['Direction'].astype(float).astype(int)
        orders_df['EntruVol'] = orders_df['EntruVol'].astype(float).astype(int)
        orders_df['DealVol'] = orders_df['DealVol'].astype(float).astype(int)
        orders_df['EntruPrice'] = orders_df['EntruPrice'].astype(float)
                 
        if direction =='all':
            return(orders_df[orders_df['Direction'].isin([0,1])])
        if direction == 'buy':
            return(orders_df[orders_df['Direction'] == 0])
        if direction == 'sell':
            return(orders_df[orders_df['Direction'] == 1])

        
    def position(self):
        '''
        当前持仓
        ['StockCode', 'SotckName','Direction','TotalSize','CoverableSize','FrozenSize','MarketValue','CostValue']
        '''
        log_helper.info('query positions')
        position_df = self._get_dataFrame(self._queryData(1))
        #log_helper.info('position_df:{0}'.format(position_df))
        
        srcCols = [u'证券代码', u'证券名称', 'Direction', u'今余额', u'可卖量', u'冻结数量', u'市值', u'买入金额']
        objCols = ['StockCode', 'SotckName','Direction','TotalSize','CoverableSize','FrozenSize','MarketValue','CostValue']

        position_df['Direction'] = 0
        if self.broker == u'东海证券':
            pass
        elif self.broker == u'东北证券':
            position_df.rename(columns = {u'参考成本价':u'成本价'}, inplace = True)
        elif self.broker == u'国联证券':
            position_df.rename(columns = {u'参考成本价':u'成本价', u'参考市值':u'最新市值'}, inplace = True)
        elif self.broker == u'东莞证券':
            position_df.rename(columns = {u'证券数量':u'今余额', u'可卖数量':u'可卖量', u'证券市值':u'市值'}, inplace = True) 
        elif self.broker in [u'国联证券', u'长城证券', u'华泰证券', u'西部证券', u'海通证券', u'东北证券', u'华福证券', u'国泰君安'
            , u'西南证券', u'同信证券', u'兴业证券']:
            position_df.rename(columns = {u'证券数量':u'今余额', u'可卖数量':u'可卖量', u'最新市值':u'市值'}, inplace = True)
        elif self.broker in [ u'中信建投']:
            position_df.rename(columns = {u'证券数量':u'今余额'
                                        , u'可卖数量':u'可卖量'
                                        , u'最新市值':u'市值'
                                        , u'买入均价':u'成本价'
                                        }
            , inplace = True)
            
        entru = self.query_active_orders(direction = 'sell')[['StockCode','EntruVol','DealVol']]

        entru['PendVol'] = entru['EntruVol'] - entru['DealVol']
        frozenSize = dict(entru.set_index('StockCode')['PendVol'])
        position_df[u'冻结数量'] = position_df[u'证券代码'].map(lambda x:frozenSize.get(x, 0))
        position_df[u'买入金额'] = position_df[u'成本价'].astype(float) * position_df[u'今余额'].astype(float)
        position_df = position_df[srcCols].rename(columns = dict(zip(srcCols, objCols)))
        for f in ['TotalSize','CoverableSize','FrozenSize']:
            position_df[f] = position_df[f].astype(float).astype(int)
        for f in ['MarketValue','CostValue']:
            position_df[f] = position_df[f].astype(float)        

        log_helper.info('query positions finish')
        return (position_df)



# //开发文档
# //

# //1.交易API均是Trade.dll文件的导出函数，包括以下函数：
# //基本版的9个函数：
# // void  OpenTdx();//打开通达信
# // void  CloseTdx();//关闭通达信
# //  int  Logon(char* IP, short Port, char* Version, short YybID, char* AccountNo,char* TradeAccount, char* JyPassword,   char* TxPassword, char* ErrInfo);//登录帐号
# // void  Logoff(int ClientID);//注销
# // void  QueryData(int ClientID, int Category, char* Result, char* ErrInfo);//查询各类交易数据
# // void  SendOrder(int ClientID, int Category ,int PriceType,  char* Gddm,  char* Zqdm , float Price, int Quantity,  char* Result, char* ErrInfo);//下单
# // void  CancelOrder(int ClientID, char* ExchangeID, char* hth, char* Result, char* ErrInfo);//撤单
# // void  GetQuote(int ClientID, char* Zqdm, char* Result, char* ErrInfo);//获取五档报价
# // void  Repay(int ClientID, char* Amount, char* Result, char* ErrInfo);//融资融券账户直接还款


# //普通批量版新增的5个函数：(有些券商对批量操作进行了限速，最大批量操作数目请咨询券商)
# // void  QueryHistoryData(int ClientID, int Category, char* StartDate, char* EndDate, char* Result, char* ErrInfo);//查询各类历史数据
# // void  QueryDatas(int ClientID, int Category[], int Count, char* Result[], char* ErrInfo[]);//单账户批量查询各类交易数据
# // void  SendOrders(int ClientID, int Category[] , int PriceType[], char* Gddm[],  char* Zqdm[] , float Price[], int Quantity[],  int Count, char* Result[], char* ErrInfo[]);//单账户批量下单
# // void  CancelOrders(int ClientID, char* ExchangeID[], char* hth[], int Count, char* Result[], char* ErrInfo[]);//单账户批量撤单
# // void  GetQuotes(int ClientID, char* Zqdm[], int Count, char* Result[], char* ErrInfo[]);//单账户批量获取五档报价


# ///交易接口执行后，如果失败，则字符串ErrInfo保存了出错信息中文说明；
# ///如果成功，则字符串Result保存了结果数据,形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。
# ///Result是\n，\t分隔的中文字符串，比如查询股东代码时返回的结果字符串就是 

# ///"股东代码\t股东名称\t帐号类别\t保留信息\n
# ///0000064567\t\t0\t\nA000064567\t\t1\t\n
# ///2000064567\t\t2\t\nB000064567\t\t3\t"

# ///查得此数据之后，通过分割字符串， 可以恢复为几行几列的表格形式的数据



# //2.API使用流程为: 应用程序先调用OpenTdx打开通达信实例，一个实例下可以同时登录多个交易账户，每个交易账户称之为ClientID.
# //通过调用Logon获得ClientID，然后可以调用其他API函数向各个ClientID进行查询或下单; 应用程序退出时应调用Logoff注销ClientID, 最后调用CloseTdx关闭通达信实例. 
# //OpenTdx和CloseTdx在整个应用程序中只能被调用一次.API带有断线自动重连功能，应用程序只需根据API函数返回的出错信息进行适当错误处理即可。


# //3. 各个函数功能说明

# /// <summary>
# /// 打开通达信实例
# /// </summary>
# ///void   OpenTdx();
# typedef void(__stdcall* OpenTdxDelegate)();


# /// <summary>
# /// 关闭通达信实例
# /// </summary>
# ///void   CloseTdx();
# typedef void(__stdcall* CloseTdxDelegate)();


# /// <summary>
# /// 交易账户登录
# /// </summary>
# /// <param name="IP">券商交易服务器IP</param>
# /// <param name="Port">券商交易服务器端口</param>
# /// <param name="Version">设置通达信客户端的版本号</param>
# /// <param name="YybID">营业部代码，请到网址 http://www.chaoguwaigua.com/downloads/qszl.htm 查询</param>
# /// <param name="AccountNo">完整的登录账号，券商一般使用资金帐户或客户号</param>
# /// <param name="TradeAccount">交易账号，一般与登录帐号相同. 请登录券商通达信软件，查询股东列表，股东列表内的资金帐号就是交易帐号, 具体查询方法请见网站“热点问答”栏目</param>
# /// <param name="JyPassword">交易密码</param>
# /// <param name="TxPassword">通讯密码</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>客户端ID，失败时返回-1</returns>
# ///  int  Logon(char* IP, short Port, char* Version,short YybID,  char* AccountNo,char* TradeAccount, char* JyPassword,   char* TxPassword, char* ErrInfo);
# typedef int(__stdcall* LogonDelegate)(char* IP, short Port, char* Version, short YybID, char* AccountNo, char* TradeAccount, char* JyPassword, char* TxPassword, char* ErrInfo);

# /// <summary>
# /// 交易账户注销
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// void  Logoff(int ClientID);
# typedef void(__stdcall* LogoffDelegate)(int ClientID);

# /// <summary>
# /// 查询各种交易数据
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Category">表示查询信息的种类，0资金  1股份   2当日委托  3当日成交     4可撤单   5股东代码  6融资余额   7融券余额  8可融证券</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">同Logon函数的ErrInfo说明</param>
# /// void  QueryData(int ClientID, int Category, char* Result, char* ErrInfo);
# typedef void(__stdcall* QueryDataDelegate)(int ClientID, int Category, char* Result, char* ErrInfo);




# /// <summary>
# /// 属于普通批量版功能,查询各种历史数据
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Category">表示查询信息的种类，0历史委托  1历史成交   2交割单</param>
# /// <param name="StartDate">表示开始日期，格式为yyyyMMdd,比如2014年3月1日为  20140301
# /// <param name="EndDate">表示结束日期，格式为yyyyMMdd,比如2014年3月1日为  20140301
# /// <param name="Result">同上</param>
# /// <param name="ErrInfo">同上</param>
# /// void  QueryHistoryData(int ClientID, int Category, char* StartDate, char* EndDate, char* Result, char* ErrInfo);
# typedef void(__stdcall* QueryHistoryDataDelegate)(int ClientID, int Category, char* StartDate, char* EndDate, char* Result, char* ErrInfo);

# /// <summary>
# /// 属于普通批量版功能,批量查询各种交易数据,用数组传入每个委托的参数，数组第i个元素表示第i个查询的相应参数
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Category">信息的种类的数组, 第i个元素表示第i个查询的信息种类，0资金  1股份   2当日委托  3当日成交     4可撤单   5股东代码  6融资余额   7融券余额  8可融证券</param>
# /// <param name="Count">查询的个数，即数组的长度</param>
# /// <param name="Result">返回数据的数组, 第i个元素表示第i个委托的返回信息. 此API执行返回后，Result[i]含义同上。</param>
# /// <param name="ErrInfo">错误信息的数组，第i个元素表示第i个委托的错误信息. 此API执行返回后，ErrInfo[i]含义同上。</param>
# /// void  QueryDatas(int ClientID, int Category[], int Count, char* Result[], char* ErrInfo[]);
# typedef void(__stdcall* QueryDatasDelegate)(int ClientID, int Category[], int Count, char* Result[], char* ErrInfo[]);



# /// <summary>
# /// 下委托交易证券
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Category">表示委托的种类，0买入 1卖出  2融资买入  3融券卖出   4买券还券   5卖券还款  6现券还券</param>
# /// <param name="PriceType">表示报价方式 0上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格  2(市价委托)深圳本方最优价格  3(市价委托)深圳即时成交剩余撤销  4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 5(市价委托)深圳全额成交或撤销 6(市价委托)上海五档即成转限价
# /// <param name="Gddm">股东代码, 交易上海股票填上海的股东代码；交易深圳的股票填入深圳的股东代码</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Price">委托价格</param>
# /// <param name="Quantity">委托数量</param>
# /// <param name="Result">同上,其中含有委托编号数据</param>
# /// <param name="ErrInfo">同上</param>
# /// void  SendOrder(int ClientID, int Category ,int PriceType,  char* Gddm,  char* Zqdm , float Price, int Quantity,  char* Result, char* ErrInfo);
# typedef void(__stdcall* SendOrderDelegate)(int ClientID, int Category, int PriceType, char* Gddm, char* Zqdm, float Price, int Quantity, char* Result, char* ErrInfo);



# /// <summary>
# /// 属于普通批量版功能,批量下委托交易证券，用数组传入每个委托的参数，数组第i个元素表示第i个委托的相应参数
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Category">委托种类的数组，第i个元素表示第i个委托的种类，0买入 1卖出  2融资买入  3融券卖出   4买券还券   5卖券还款  6现券还券</param>
# /// <param name="PriceType">表示报价方式的数组,  第i个元素表示第i个委托的报价方式, 0上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格  2(市价委托)深圳本方最优价格  3(市价委托)深圳即时成交剩余撤销  4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 5(市价委托)深圳全额成交或撤销 6(市价委托)上海五档即成转限价
# /// <param name="Gddm">股东代码数组，第i个元素表示第i个委托的股东代码，交易上海股票填上海的股东代码；交易深圳的股票填入深圳的股东代码</param>
# /// <param name="Zqdm">证券代码数组，第i个元素表示第i个委托的证券代码</param>
# /// <param name="Price">委托价格数组，第i个元素表示第i个委托的委托价格</param>
# /// <param name="Quantity">委托数量数组，第i个元素表示第i个委托的委托数量</param>
# /// <param name="Count">委托的个数，即数组的长度</param>
# /// <param name="Result">同上</param>
# /// <param name="ErrInfo">同上</param>
# /// void  SendOrders(int ClientID, int Category[] , int PriceType[], char* Gddm[],  char* Zqdm[] , float Price[], int Quantity[],  int Count, char* Result[], char* ErrInfo[]);
# typedef void(__stdcall* SendOrdersDelegate)(int ClientID, int Category[], int PriceType[], char* Gddm[], char* Zqdm[], float Price[], int Quantity[], int Count, char* Result[], char* ErrInfo[]);



# /// <summary>
# /// 撤委托
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="ExchangeID">交易所ID， 上海1，深圳0(招商证券普通账户深圳是2)</param>
# /// <param name="hth">表示要撤的目标委托的编号</param>
# /// <param name="Result">同上</param>
# /// <param name="ErrInfo">同上</param>
# /// void  CancelOrder(int ClientID, char* ExchangeID, char* hth, char* Result, char* ErrInfo);
# typedef void(__stdcall* CancelOrderDelegate)(int ClientID, char* ExchangeID, char* hth, char* Result, char* ErrInfo);




# /// <summary>
# /// 属于普通批量版功能,批量撤委托, 用数组传入每个委托的参数，数组第i个元素表示第i个撤委托的相应参数
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# // <param name="ExchangeID">交易所ID， 上海1，深圳0(招商证券普通账户深圳是2)</param>
# /// <param name="hth">表示要撤的目标委托的编号</param>
# /// <param name="Count">撤委托的个数，即数组的长度</param>
# /// <param name="Result">同上</param>
# /// <param name="ErrInfo">同上</param>
# /// void  CancelOrders(int ClientID, char* ExchangeID[], char* hth[], int Count, char* Result[], char* ErrInfo[]);
# typedef void(__stdcall* CancelOrdersDelegate)(int ClientID, char* ExchangeID[], char* hth[], int Count, char* Result[], char* ErrInfo[]);




# /// <summary>
# /// 获取证券的实时五档行情
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Result">同上</param>
# /// <param name="ErrInfo">同上</param>
# /// void  GetQuote(int ClientID, char* Zqdm, char* Result, char* ErrInfo);
# typedef void(__stdcall* GetQuoteDelegate)(int ClientID, char* Zqdm, char* Result, char* ErrInfo);


# /// <summary>
# /// 属于普通批量版功能,批量获取证券的实时五档行情
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Result">同上</param>
# /// <param name="ErrInfo">同上</param>
# /// void  GetQuotes(int ClientID, char* Zqdm[], int Count, char* Result[], char* ErrInfo[]);
# typedef void(__stdcall* GetQuotesDelegate)(int ClientID, char* Zqdm[], int Count, char* Result[], char* ErrInfo[]);



# /// <summary>
# /// 融资融券直接还款
# /// </summary>
# /// <param name="ClientID">客户端ID</param>
# /// <param name="Amount">还款金额</param>
# /// <param name="Result">同上</param>
# /// <param name="ErrInfo">同上</param>
# /// void  Repay(int ClientID, char* Amount, char* Result, char* ErrInfo);
# typedef void(__stdcall* RepayDelegate)(int ClientID, char* Amount, char* Result, char* ErrInfo);





# int _tmain(int argc, _TCHAR* argv[])
# {
# 	//载入dll, 所有4个dll都要复制到debug和release目录下,必须采用多字节字符集编程设置
# 	HMODULE HMODULE1 = LoadLibrary("Trade.dll");

# 	//获取api函数
# 	OpenTdxDelegate OpenTdx = (OpenTdxDelegate)GetProcAddress(HMODULE1, "OpenTdx");
# 	CloseTdxDelegate CloseTdx = (CloseTdxDelegate)GetProcAddress(HMODULE1, "CloseTdx");
# 	LogonDelegate Logon = (LogonDelegate)GetProcAddress(HMODULE1, "Logon");
# 	LogoffDelegate Logoff = (LogoffDelegate)GetProcAddress(HMODULE1, "Logoff");
# 	QueryDataDelegate QueryData = (QueryDataDelegate)GetProcAddress(HMODULE1, "QueryData");
# 	SendOrderDelegate SendOrder = (SendOrderDelegate)GetProcAddress(HMODULE1, "SendOrder");
# 	CancelOrderDelegate CancelOrder = (CancelOrderDelegate)GetProcAddress(HMODULE1, "CancelOrder");
# 	GetQuoteDelegate GetQuote = (GetQuoteDelegate)GetProcAddress(HMODULE1, "GetQuote");
# 	RepayDelegate Repay = (RepayDelegate)GetProcAddress(HMODULE1, "Repay");


# 	//以下是普通批量版功能函数
# 	QueryDatasDelegate QueryDatas = (QueryDatasDelegate)GetProcAddress(HMODULE1, "QueryDatas");
# 	QueryHistoryDataDelegate QueryHistoryData = (QueryHistoryDataDelegate)GetProcAddress(HMODULE1, "QueryHistoryData");
# 	SendOrdersDelegate SendOrders = (SendOrdersDelegate)GetProcAddress(HMODULE1, "SendOrders");
# 	CancelOrdersDelegate CancelOrders = (CancelOrdersDelegate)GetProcAddress(HMODULE1, "CancelOrders");
# 	GetQuotesDelegate GetQuotes = (GetQuotesDelegate)GetProcAddress(HMODULE1, "GetQuotes");

# 	////以下是高级批量版功能函数
# 	//QueryMultiAccountsDatasDelegate QueryMultiAccountsDatas = (QueryMultiAccountsDatasDelegate)GetProcAddress(HMODULE1, "QueryMultiAccountsDatas");
# 	//SendMultiAccountsOrdersDelegate SendMultiAccountsOrders = (SendMultiAccountsOrdersDelegate)GetProcAddress(HMODULE1, "SendMultiAccountsOrders");
# 	//CancelMultiAccountsOrdersDelegate CancelMultiAccountsOrders = (CancelMultiAccountsOrdersDelegate)GetProcAddress(HMODULE1, "CancelMultiAccountsOrders");
# 	//GetMultiAccountsQuotesDelegate GetMultiAccountsQuotes = (GetMultiAccountsQuotesDelegate)GetProcAddress(HMODULE1, "GetMultiAccountsQuotes");


# 	//开始交易
# 	char* Result = new char[1024 * 1024];
# 	char* ErrInfo = new char[256];



# 	OpenTdx();//打开通达信,OpenTdx在整个应用程序中只能被调用一次,不能多次调用


# 	//登录帐号2
# 	int ClientID = Logon("61.132.54.83", 7708, "6.0", 0, "666623424243", "666623424243", "147369", "147258",ErrInfo);

# 	//登录第二个帐号
# 	//int ClientID2 = Logon("111.111.111.111", 7708, "4.20", 0, "33333333","33333333",  "333", "", ErrInfo);
# 	if (ClientID == -1)
# 	{
# 		cout << ErrInfo << endl;//登录失败
# 	}
# 	else
# 	{
# 		//登录成功
# 		QueryData(ClientID, 0, Result, ErrInfo);//查询资金
# 		//QueryData(ClientID2, 0, Result, ErrInfo);//第二个帐号,查询资金
# 		cout << "查询资金结果:" << Result << " " << ErrInfo;
# 		//SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.898, 100, "", "");
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.910f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.911f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.912f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.913f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.914f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.915f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.916f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.917f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.918f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.919f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.910f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.911f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.912f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.913f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.914f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.915f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.916f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.917f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.918f, 100, Result, ErrInfo);
# 		SendOrder(ClientID, 1, 0, "0190061463", "150153", 0.919f, 100, Result, ErrInfo);

# 		//CancelOrder(ClientID, 0, "1480", Result, ErrInfo);//撤单
# 		//SendOrders(ClientID, 1, 0, "0190061463", "150153", 0.920f, 100, 5, Result, ErrInfo);//单账户批量下单
# 		cout << "查询资金结果:" << Result << " " << ErrInfo;

# 		Logoff(ClientID);//注销
# 	}


# 	delete[] Result;
# 	delete[] ErrInfo;



# 	FreeLibrary(HMODULE1);

# 	return 0;
# }
